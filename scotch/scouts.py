from urllib.parse import urlparse
try:
    from ddgs import DDGS
except Exception:
    DDGS = None
from .models import Candidate

def _search(q, max_results=8):
    if DDGS is None:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt")
    out=[]
    with DDGS() as d:
        for r in d.text(q, max_results=max_results):
            out.append(Candidate(company=_host_label(r.get("href","")), role=r.get("title",""), url=r.get("href",""), snippet=r.get("body",""), source="open web"))
    return out

def _host_label(url):
    h=urlparse(url).netloc.replace("www.","")
    bits=h.split(".")
    return (bits[0] if bits else h).replace("-"," ").title()

def frontier_queries(lens):
    geo=" OR ".join(f'"{x}"' for x in lens.get("geography",["Canada"]))
    roles=" OR ".join(f'"{x}"' for x in lens.get("target_levels",[])[:4])
    return [
        f'({roles}) ({geo}) ("own the product" OR "product strategy" OR "end-to-end" OR roadmap)',
        f'({roles}) ({geo}) ("0-to-1" OR "new product" OR "product line" OR "full lifecycle")',
        f'({roles}) ({geo}) (discovery roadmap launch adoption)']

def adjacency_queries(lens):
    geo=" OR ".join(f'"{x}"' for x in lens.get("geography",["Canada"]))
    domains=lens.get("adjacency_interests",[]) + lens.get("industry_interests",[])
    pairs=[]
    for i in range(0,len(domains),2):
        pair=domains[i:i+2]
        if pair: pairs.append(" OR ".join(f'"{x}"' for x in pair))
    return [f'("Senior Product Manager" OR "Staff Product Manager" OR "Lead Product Manager") ({geo}) ({p}) ("roadmap" OR "product strategy")' for p in pairs[:5]]

def venture_queries(lens):
    geo=" OR ".join(f'"{x}"' for x in lens.get("geography",["Canada"]))
    return [
        f'("Senior Product Manager" OR "Staff Product Manager") ({geo}) (startup OR "Series A" OR "Series B" OR equity) ("0-to-1" OR ownership)',
        f'("first product manager" OR "first PM" OR "founding product") ({geo}) (equity OR founder OR startup)',
        f'("Senior Product Manager" OR "Lead Product Manager") ({geo}) ("high growth" OR "fast-growing") ("own" OR roadmap)']

def run_scouts(lens, per_query=7):
    bundles=[("frontier",frontier_queries(lens)),("adjacency",adjacency_queries(lens)),("venture",venture_queries(lens))]
    seen={}
    for scout,queries in bundles:
        for q in queries:
            for c in _search(q,per_query):
                if not c.url: continue
                if c.url in seen:
                    if scout not in seen[c.url].discovery_reason: seen[c.url].discovery_reason += f", {scout}"
                    continue
                c.discovery_reason=scout; seen[c.url]=c
    return list(seen.values())
