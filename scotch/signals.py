import re

OWNERSHIP = ["own the product","own product","own the roadmap","own the strategy","product vision","product strategy","product direction","end-to-end","end to end","full lifecycle","0-to-1","0 to 1","new product line","accountable for","from discovery through","from concept through","from concept to","from idea to","drive the roadmap","define the roadmap"]
DISCOVERY = ["customer discovery","user research","customer research","discovery","problem definition","market research","competitive research"]
BUILD = ["roadmap","prioritization","product requirements","design","engineering","launch","go-to-market","gtm","adoption","iterate","iteration","experimentation","metrics"]
VENTURE = ["series a","series b","series c","startup","scale-up","scale up","equity","venture-backed","venture backed","founder","first product manager","first pm","founding product","high growth","fast-growing","fast growing"]
PLATFORM_HEAVY = ["developer platform","infrastructure platform","internal platform","platform enablement","api product","integration platform","identity platform","authorization platform"]
PEOPLE_MGMT = ["manage product managers","managing product managers","lead a team of product managers","hire and develop product managers"]
PLM_ADJ = ["plm","product lifecycle","qms","quality management","manufacturing","bom","bill of materials","engineering change","supply chain","lims","mes","erp","industrial software"]
FIN = ["fintech","payments","banking","wealth","lending","mortgage","credit","financial services","expense","spend management","payout","reconciliation","underwriting"]
HOSP = ["hospitality","travel","restaurant","booking","hotel","tour","attraction","guest","flight","vacation","reservation"]
AI = ["agentic","generative ai","artificial intelligence","llm","machine learning","copilot","rag"]

def count(blob, terms):
    b=blob.lower()
    return sum(1 for t in terms if t in b)

def evidence_lines(blob, terms, limit=3):
    compact=re.sub(r'\s+',' ',blob or '').strip()
    if not compact: return []
    sentences=re.split(r'(?<=[.!?])\s+',compact)
    out=[]
    for s in sentences:
        low=s.lower()
        if any(t in low for t in terms):
            s=s.strip()
            if 35 <= len(s) <= 340 and s not in out: out.append(s)
        if len(out)>=limit: break
    return out

def infer_domain(blob):
    scores={"Industrial / PLM":count(blob,PLM_ADJ),"Finance / Fintech":count(blob,FIN),"Travel / Hospitality":count(blob,HOSP),"AI Product":count(blob,AI)}
    label,score=max(scores.items(),key=lambda kv:kv[1])
    if score: return label
    if any(x in blob.lower() for x in ["b2b","saas","enterprise software"]): return "B2B SaaS"
    return "Other"
