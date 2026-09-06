from urllib.parse import urlparse
try:
    from ddgs import DDGS
except Exception:
    DDGS = None
from .models import Candidate

def _search(q,max_results=7):
    if DDGS is None: raise RuntimeError("Install dependencies with: pip install -r requirements.txt")
    out=[]
    with DDGS() as d:
        for r in d.text(q,max_results=max_results):
            out.append(Candidate(company=_host_label(r.get("href","")),role=r.get("title",""),url=r.get("href",""),snippet=r.get("body",""),source="open web"))
    return out

def _host_label(url):
    h=urlparse(url).netloc.replace("www.",""); parts=h.split(".")
    return (parts[0] if parts else h).replace("-"," ").title()

def _geo(lens): return " OR ".join(f'"{x}"' for x in lens.get("geography",["Canada"]))
def _roles(lens):
    levels=lens.get("target_levels",[])
    return " OR ".join(f'"{x}"' for x in levels[:5]) or '"Senior Product Manager" OR "Staff Product Manager"'

def frontier_queries(lens):
    r,g=_roles(lens),_geo(lens)
    return [f'({r}) ({g}) ("own the product" OR "own the roadmap" OR "product strategy")',f'({r}) ({g}) ("0-to-1" OR "new product line" OR "from discovery through launch")',f'({r}) ({g}) ("customer discovery" roadmap launch adoption)',f'({r}) ({g}) ("full lifecycle" OR "end-to-end") product']

def adjacency_queries(lens):
    r,g=_roles(lens),_geo(lens); domains=lens.get("adjacency_interests",[])+lens.get("industry_interests",[]); q=[]
    for i in range(0,min(len(domains),12),2):
        pair=domains[i:i+2]
        if pair:
            p=" OR ".join(f'"{x}"' for x in pair); q.append(f'({r}) ({g}) ({p}) (roadmap OR discovery OR launch)')
    return q[:6]

def venture_queries(lens):
    r,g=_roles(lens),_geo(lens)
    return [f'({r}) ({g}) (startup OR "Series A" OR "Series B" OR "Series C") (equity OR ownership)',f'("first product manager" OR "first PM" OR "founding product") ({g})',f'({r}) ({g}) ("fast-growing" OR "high growth" OR "venture-backed") ("new product" OR roadmap)']

def wildcard_queries(lens):
    g=_geo(lens)
    return [f'("Staff Product Manager" OR "Lead Product Manager" OR "Senior Product Manager") ({g}) ("you will own" OR "you’ll own")',f'("Principal Product Manager" OR "Staff Product Manager") ({g}) ("from concept to launch" OR "from discovery to launch")',f'("Senior Product Manager") ({g}) ("reports to the CEO" OR "work directly with founders")']

def run_scouts(lens,per_query=6):
    bundles=[("open market",frontier_queries(lens)),("adjacent",adjacency_queries(lens)),("startup",venture_queries(lens)),("wildcard",wildcard_queries(lens))]; seen={}
    for scout,queries in bundles:
        for q in queries:
            for c in _search(q,per_query):
                if not c.url: continue
                if c.url in seen:
                    if scout not in seen[c.url].discovery_reason: seen[c.url].discovery_reason += f" · {scout}"
                    continue
                c.discovery_reason=scout; seen[c.url]=c
    return list(seen.values())
