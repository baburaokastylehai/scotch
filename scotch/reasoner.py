import re
from .models import Assessment, Candidate
from .signals import OWNERSHIP,DISCOVERY,BUILD,VENTURE,PLATFORM_HEAVY,PEOPLE_MGMT,count,evidence_lines

LEVEL={"principal":99,"staff":97,"lead":93,"senior":88,"product manager iii":84,"product manager ii":78,"product manager":73}
DOMAIN_TERMS={
    "finance":["lending","banking","payments","fintech","financial services","mortgage","credit","underwriting"],
    "travel":["travel","hospitality","hotel","booking","restaurant","airline"],
    "industrial":["plm","qms","manufacturing","supply chain","logistics","erp","mes","lims"]
}

def _level(role):
    r=role.lower()
    for k,v in LEVEL.items():
        if k in r: return v
    return 70

def _profile_text(lens):
    return " ".join(lens.get("evidence",[])).lower()

def _has_profile_domain(lens, family):
    p=_profile_text(lens)
    return any(t in p for t in DOMAIN_TERMS[family])

def _hard_requirement_gap(blob,lens):
    b=re.sub(r'\s+',' ',blob.lower())
    # Domain-specific experience only becomes a hard gap when the JD frames it as required/minimum.
    for family,terms in DOMAIN_TERMS.items():
        if _has_profile_domain(lens,family):
            continue
        for term in terms:
            patterns=[
                rf'(?:minimum|at least|must have|required|requires?)\s+[^.\n]{{0,90}}(?:year|years)[^.\n]{{0,120}}\b{re.escape(term)}\b',
                rf'(?:\d+\+?\s*(?:-|–)?\s*(?:\d+\+?\s*)?years?)[^.\n]{{0,100}}\b{re.escape(term)}\b[^.\n]{{0,70}}(?:experience|required|must)',
                rf'\b{re.escape(term)}\b[^.\n]{{0,80}}(?:experience)[^.\n]{{0,60}}(?:required|must|minim(?:um|ally))'
            ]
            if any(re.search(p,b,re.I) for p in patterns):
                return f"requires prior {family} domain experience you haven't established"
    return ""

def _domain_transfer(c,lens,b):
    # Transfer is evidence-based. Interest in a domain is not evidence of experience in it.
    profile=_profile_text(lens)
    score=58
    own_h=count(b,OWNERSHIP); disc_h=count(b,DISCOVERY); build_h=count(b,BUILD)
    if own_h>=2: score+=10
    if disc_h>=1: score+=6
    if build_h>=3: score+=6
    if c.domain=="Industrial / PLM" and any(t in profile for t in DOMAIN_TERMS["industrial"]): score+=14
    if c.domain=="Finance / Fintech" and _has_profile_domain(lens,"finance"): score+=14
    if c.domain=="Travel / Hospitality" and _has_profile_domain(lens,"travel"): score+=14
    if c.domain=="AI Product" and any(t in profile for t in ["ai","llm","agent","machine learning"]): score+=8
    return min(100,score)

def assess(c: Candidate,lens) -> Assessment:
    b=" ".join([c.role,c.snippet,c.page_text,c.domain]).lower()
    own_h=count(b,OWNERSHIP); disc_h=count(b,DISCOVERY); build_h=count(b,BUILD); venture_h=count(b,VENTURE); platform_h=count(b,PLATFORM_HEAVY); mgmt_h=count(b,PEOPLE_MGMT)
    gap=_hard_requirement_gap(b,lens)
    ownership=min(100,38+own_h*9+disc_h*4+build_h*2)
    transfer=_domain_transfer(c,lens,b)
    lvl=_level(c.role)
    step_up=min(100,round(.56*lvl+.44*ownership))
    optionality=min(100,48+(10 if c.domain!="Other" else 0)+min(20,build_h*3)+(8 if disc_h else 0)+(8 if own_h>=3 else 0))
    venture=min(100,38+venture_h*11+(6 if c.compensation else 0))
    risk=min(100,28+platform_h*15+mgmt_h*11+(12 if transfer<70 else 0)+(12 if ownership<65 else 0)+(38 if gap else 0))
    signal=round(.32*ownership+.20*transfer+.20*step_up+.13*optionality+.08*venture-.13*risk)
    if gap: signal=min(signal,49)
    signal=max(0,min(100,signal))

    ev=evidence_lines(c.page_text or c.snippet,OWNERSHIP+DISCOVERY+BUILD,2)
    if gap:
        why_this="not a fit"
        what_you_own="scope may be interesting, but the requirement mismatch is decisive."
        what_carries="your product craft transfers; the required domain history does not."
        critique=gap+"."
        recommendation="pass"
    else:
        why_this=_why_this(c,ownership,step_up,optionality)
        what_you_own=_what_you_own(ownership,own_h)
        what_carries=_what_carries(c,lens)
        critique=_critic(ownership,platform_h,mgmt_h,transfer,c)
        recommendation="pursue" if signal>=80 else "inspect" if signal>=68 else "maybe" if signal>=60 else "pass"
    stretch=""
    return Assessment(ownership,transfer,step_up,optionality,venture,risk,signal,why_this,what_you_own,what_carries,stretch,critique,recommendation,ev)

def _what_you_own(o,oh):
    if o>=86 and oh>=3: return "clear end-to-end product ownership."
    if o>=72: return "meaningful ownership; verify the exact decision boundary."
    return "ownership is too diffuse to call this a strong move."

def _what_carries(c,lens):
    if c.domain=="Industrial / PLM": return "enterprise workflows, lifecycle complexity, roadmap ownership."
    if c.domain=="Finance / Fintech": return "enterprise product judgment transfers; domain depth still needs scrutiny."
    if c.domain=="Travel / Hospitality": return "end-to-end product ownership transfers cleanly."
    if c.domain=="AI Product": return "product strategy plus hands-on AI building can transfer."
    return "discovery, strategy, roadmap, and shipped enterprise outcomes."

def _critic(o,ph,mh,t,c):
    if ph: return "too platform/infrastructure-heavy unless the customer product boundary is stronger than it reads."
    if mh: return "may include PM people management; verify this is really an IC ownership role."
    if o<70: return "the JD shows participation more clearly than accountability."
    if t<68: return "domain transfer is plausible, but not yet proven."
    if not c.compensation: return "scope looks plausible; compensation and decision rights still need checking."
    return "no obvious structural mismatch from the JD."

def _why_this(c,o,s,opt):
    if o>=84 and s>=82: return "bigger ownership without changing the kind of PM work you do best."
    if o>=78: return "the ownership shape is stronger than the title alone suggests."
    if s>=86: return "a credible step-up if the scope is as real as the title."
    if opt>=76: return "not obvious, but it could widen your next set of options."
    return "worth a closer look, but not yet a standout."
