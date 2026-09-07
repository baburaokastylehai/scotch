from urllib.parse import urlparse
try:
    from ddgs import DDGS
except Exception:
    DDGS = None
from .models import Candidate

ATS_HOSTS=("jobs.ashbyhq.com","job-boards.greenhouse.io","boards.greenhouse.io","jobs.lever.co")
BLOCKED_HOSTS=("indeed.com","linkedin.com","glassdoor.com","jobgether.com")

def _search(q,max_results=7):
    if DDGS is None: raise RuntimeError("Install dependencies with: pip install -r requirements.txt")
    out=[]
    with DDGS() as d:
        for r in d.text(q,max_results=max_results):
            url=r.get("href","") or ""
            if not _good_url(url):
                continue
            out.append(Candidate(company=_company_from_url(url),role=r.get("title","") or "",url=url,snippet=r.get("body","") or "",source="open web"))
    return out

def _good_url(url):
    if not url: return False
    p=urlparse(url); h=p.netloc.lower().replace("www.",""); path=p.path.lower()
    if any(b in h for b in BLOCKED_HOSTS): return False
    if path.rstrip("/").endswith("/apply"): return False
    return True

def _company_from_url(url):
    p=urlparse(url); h=p.netloc.lower().replace("www.",""); parts=[x for x in p.path.split("/") if x]
    if h=="jobs.ashbyhq.com" and parts: return parts[0].replace("-"," ").title()
    if h=="jobs.lever.co" and parts: return parts[0].replace("-"," ").title()
    if "greenhouse.io" in h and parts: return parts[0].replace("-"," ").title()
    host=h.split(".")[0] if h else ""
    return host.replace("-"," ").title()

def _geo(lens):
    places=[]
    for x in lens.get("geography",["Canada"]):
        if x not in places: places.append(x)
    return " OR ".join(f'"{x}"' for x in places[:3])

def _roles(lens):
    levels=lens.get("target_levels",[])
    return " OR ".join(f'"{x}"' for x in levels[:4]) or '"Senior Product Manager" OR "Staff Product Manager"'

def frontier_queries(lens):
    r,g=_roles(lens),_geo(lens)
    return [f'({r}) ({g}) ("own" roadmap launch)',f'({r}) ({g}) ("end-to-end" OR "0 to 1" OR "new product")']

def ats_queries(lens):
    g=_geo(lens)
    return [
      f'("Senior Product Manager" OR "Staff Product Manager") ({g}) site:jobs.ashbyhq.com',
      f'("Senior Product Manager" OR "Lead Product Manager") ({g}) site:jobs.lever.co',
      f'("Senior Product Manager" OR "Principal Product Manager") ({g}) site:job-boards.greenhouse.io'
    ]

def adjacency_queries(lens):
    g=_geo(lens); domains=lens.get("industry_interests",[])
    useful=[x for x in domains if len(x)<24][:6]
    if not useful: return []
    terms=" OR ".join(f'"{x}"' for x in useful)
    return [f'("Senior Product Manager" OR "Staff Product Manager") ({g}) ({terms})']

def venture_queries(lens):
    g=_geo(lens)
    return [f'("Senior Product Manager" OR "Lead Product Manager") ({g}) (startup OR "Series A" OR "Series B") (roadmap OR ownership)']

def wildcard_queries(lens):
    g=_geo(lens)
    return [f'("Staff Product Manager" OR "Principal Product Manager") ({g}) ("you will own" OR "concept to launch")']

def run_scouts(lens,per_query=5,quick=False):
    bundles=[("live ATS",ats_queries(lens)),("open market",frontier_queries(lens)),("adjacent",adjacency_queries(lens)),("startup",venture_queries(lens)),("wildcard",wildcard_queries(lens))]
    if quick:
        bundles=[("live ATS",ats_queries(lens)[:3])]
        per_query=min(per_query,4)
    seen={}
    for scout,queries in bundles:
        for q in queries:
            try: results=_search(q,per_query)
            except Exception: continue
            for c in results:
                low=(c.role+" "+c.snippet).lower()
                if "product manager" not in low and "product lead" not in low: continue
                if c.url in seen:
                    if scout not in seen[c.url].discovery_reason: seen[c.url].discovery_reason += f" · {scout}"
                    continue
                c.discovery_reason=scout; seen[c.url]=c
    return list(seen.values())
