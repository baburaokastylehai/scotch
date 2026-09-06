from .models import Assessment, Candidate
from .signals import OWNERSHIP,DISCOVERY,BUILD,VENTURE,PLATFORM_HEAVY,PEOPLE_MGMT,count,evidence_lines
LEVEL={"principal":99,"staff":97,"lead":93,"senior":88,"product manager iii":84,"product manager ii":78,"product manager":73}

def _level(role):
    r=role.lower()
    for k,v in LEVEL.items():
        if k in r: return v
    return 70

def _domain_transfer(c,lens,b):
    interests=" ".join(lens.get("industry_interests",[])+lens.get("adjacency_interests",[])).lower(); score=58
    if c.domain.lower() in interests: score+=18
    desired=[x.lower() for x in lens.get("desired_ownership",[])]
    if any("own" in x for x in desired) and count(b,OWNERSHIP)>=2: score+=10
    if count(b,DISCOVERY)>=1: score+=6
    if count(b,BUILD)>=3: score+=6
    return min(100,score)

def assess(c: Candidate,lens) -> Assessment:
    b=" ".join([c.role,c.snippet,c.page_text,c.domain]).lower(); own_h=count(b,OWNERSHIP); disc_h=count(b,DISCOVERY); build_h=count(b,BUILD); venture_h=count(b,VENTURE); platform_h=count(b,PLATFORM_HEAVY); mgmt_h=count(b,PEOPLE_MGMT)
    ownership=min(100,38+own_h*9+disc_h*4+build_h*2); transfer=_domain_transfer(c,lens,b); lvl=_level(c.role); step_up=min(100,round(.56*lvl+.44*ownership)); optionality=min(100,50+(10 if c.domain!="Other" else 0)+min(24,build_h*3)+(8 if disc_h else 0)+(8 if own_h>=3 else 0)); venture=min(100,40+venture_h*11+(8 if c.compensation else 0)); risk=min(100,32+platform_h*15+mgmt_h*11+(10 if transfer<70 else 0)+(10 if ownership<65 else 0))
    signal=round(.30*ownership+.17*transfer+.19*step_up+.15*optionality+.10*venture-.09*risk); signal=max(0,min(100,signal)); ev=evidence_lines(c.page_text or c.snippet,OWNERSHIP+DISCOVERY+BUILD,3)
    what_you_own=_what_you_own(ownership,own_h); what_carries=_what_carries(c); stretch=_stretch(transfer,venture,lvl); critique=_critic(ownership,platform_h,mgmt_h,transfer,risk,c); why_this=_why_this(c,ownership,step_up,optionality,venture); recommendation="pursue" if signal>=82 else "inspect" if signal>=69 else "maybe" if signal>=58 else "pass"
    return Assessment(ownership,transfer,step_up,optionality,venture,risk,signal,why_this,what_you_own,what_carries,stretch,critique,recommendation,ev)

def _what_you_own(o,oh):
    if o>=86 and oh>=3: return "Reads like real product ownership: problem → strategy → roadmap → build → launch/iteration."
    if o>=72: return "There is meaningful ownership here, but the exact boundary of the product area should be verified."
    return "The JD talks about product work, but it does not yet prove that you own a coherent product or initiative."
def _what_carries(c):
    if c.domain=="Industrial / PLM": return "Complex B2B workflows, lifecycle thinking, enterprise customers, roadmap ownership, and change-heavy product problems transfer directly."
    if c.domain=="Finance / Fintech": return "Enterprise workflow/product judgment transfers; financial-domain depth is the main story you would need to build."
    if c.domain=="Travel / Hospitality": return "End-to-end product ownership transfers well; the domain changes, but the product motion stays familiar."
    if c.domain=="AI Product": return "Product strategy, enterprise workflows, and hands-on AI-building evidence can transfer; production AI depth may still be a gap."
    return "The strongest transferable story is ownership: discovery, strategy, roadmap, cross-functional execution, and shipped outcomes."
def _stretch(t,v,lvl):
    if lvl>=96: return "A real level stretch. Worth it only if the scope is genuinely Staff/Principal rather than title inflation."
    if v>=72: return "The stretch is company-stage ambiguity: more upside and ownership, but more execution and business risk."
    if t<70: return "The stretch is domain credibility, not product craft."
    return "Reasonable stretch: enough new surface area to grow without asking for a different kind of PM."
def _critic(o,ph,mh,t,risk,c):
    issues=[]
    if ph: issues.append("Watch the ownership boundary: parts of this role read platform/infrastructure-heavy.")
    if mh: issues.append("There is PM people-management language; verify this is an IC/product-owner role if that matters.")
    if o<70: issues.append("The JD may be broad product participation rather than true end-to-end accountability.")
    if t<68: issues.append("A crisp domain-transfer narrative would be needed.")
    if not c.compensation: issues.append("Compensation is not visible yet.")
    return " ".join(issues) if issues else "No structural red flag from the JD. The next questions are manager quality, company momentum, actual decision rights, and compensation."
def _why_this(c,o,s,opt,v):
    bits=[]
    if o>=80: bits.append("high ownership")
    if s>=84: bits.append("step-up scope")
    if opt>=78: bits.append("good future optionality")
    if v>=72: bits.append("startup/upside signal")
    if c.domain!="Other": bits.append(c.domain.lower())
    return "Interesting because of "+", ".join(bits[:4])+"." if bits else "Potentially relevant, but not yet a standout move."
