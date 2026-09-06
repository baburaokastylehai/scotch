from .models import Assessment, Candidate

OWN=["own the product","own product","own the roadmap","product strategy","product vision","end-to-end","end to end","full lifecycle","0-to-1","0 to 1","new product line","accountable for","product direction"]
BUILD=["customer discovery","discovery","user research","roadmap","priorit","launch","adoption","iterate","iteration","go-to-market","gtm","metrics"]
VENTURE=["series a","series b","series c","startup","equity","first product manager","first pm","founder","venture-backed","fast-growing","high growth"]
ANTI=["api product manager","integration product manager","developer platform","infrastructure product manager","technical program manager"]
LEVEL={"principal":98,"staff":96,"lead":92,"senior":87,"product manager iii":84,"product manager":73}

def hits(blob, terms): return sum(1 for t in terms if t in blob)

def assess(c: Candidate, lens) -> Assessment:
    b=" ".join([c.role,c.snippet,c.page_text,c.domain]).lower()
    oh,bh,vh,ah=hits(b,OWN),hits(b,BUILD),hits(b,VENTURE),hits(b,ANTI)
    ownership=min(100,35+oh*10+bh*3)
    transfer=62
    interests=" ".join(lens.get("industry_interests",[])+lens.get("adjacency_interests",[])).lower()
    if c.domain.lower() in interests or any(w.lower() in b for w in lens.get("industry_interests",[])): transfer+=14
    if bh>=3: transfer+=8
    transfer=min(100,transfer)
    lvl=73
    for k,v in LEVEL.items():
        if k in c.role.lower(): lvl=v; break
    step_up=min(100, round(.55*lvl+.45*ownership))
    optionality=min(100,52+(10 if c.domain not in ["Other"] else 0)+min(22,bh*3)+(8 if "new product" in b else 0))
    venture=min(100,42+vh*11+(8 if c.compensation else 0))
    risk=min(100,38+ah*16+(10 if transfer<70 else 0)+(8 if ownership<65 else 0))
    score=max(0,min(100,round(.30*ownership+.17*transfer+.18*step_up+.16*optionality+.10*venture-.09*risk)))
    interpretation=("Strong ownership signal. " if ownership>=80 else "Ownership needs closer inspection. ") + ("Evidence appears transferable. " if transfer>=75 else "This requires a meaningful adjacency jump. ") + ("Scope reads as a plausible step-up rather than a lateral move." if step_up>=82 else "")
    issues=[]
    if ah: issues.append("Could be infrastructure/platform work disguised as broader product ownership.")
    if ownership<65: issues.append("The posting does not yet prove meaningful end-to-end ownership.")
    if transfer<70: issues.append("Domain transfer needs evidence rather than assumption.")
    if not issues: issues.append("No obvious structural red flag; verify team scope, decision rights, compensation, and company quality.")
    recommendation="Pursue" if score>=82 else "Inspect" if score>=68 else "Watch" if score>=58 else "Pass"
    return Assessment(ownership,transfer,step_up,optionality,venture,risk,score,interpretation," ".join(issues),recommendation)
