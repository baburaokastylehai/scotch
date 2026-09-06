from urllib.parse import urlparse
try:
    from ddgs import DDGS
except Exception:
    DDGS = None
from .models import Candidate

ATS_HOSTS = (
    "jobs.ashbyhq.com",
    "job-boards.greenhouse.io",
    "boards.greenhouse.io",
    "jobs.lever.co",
)

def _search(q,max_results=7):
    if DDGS is None:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt")
    out=[]
    with DDGS() as d:
        for r in d.text(q,max_results=max_results):
            out.append(Candidate(
                company=_host_label(r.get("href","")),
                role=r.get("title",""),
                url=r.get("href",""),
                snippet=r.get("body",""),
                source="open web"
            ))
    return out

def _host_label(url):
    h=urlparse(url).netloc.replace("www.","")
    parts=h.split(".")
    return (parts[0] if parts else h).replace("-"," ").title()

def _geo(lens):
    places=lens.get("geography",["Canada"])
    # Search engines handle a small geography expression much more reliably
    # than a long OR chain.
    preferred=[]
    for x in places:
        if x not in preferred:
            preferred.append(x)
    return " OR ".join(f'"{x}"' for x in preferred[:3])

def _roles(lens):
    levels=lens.get("target_levels",[])
    return " OR ".join(f'"{x}"' for x in levels[:4]) or '"Senior Product Manager" OR "Staff Product Manager"'

def frontier_queries(lens):
    r,g=_roles(lens),_geo(lens)
    return [
        f'({r}) ({g}) (ownership OR roadmap OR discovery OR launch)',
        f'({r}) ({g}) ("0 to 1" OR "new product" OR "end-to-end")',
    ]

def ats_queries(lens):
    g=_geo(lens)
    return [
        f'("Senior Product Manager" OR "Staff Product Manager") ({g}) site:jobs.ashbyhq.com',
        f'("Senior Product Manager" OR "Lead Product Manager") ({g}) site:job-boards.greenhouse.io',
        f'("Senior Product Manager" OR "Principal Product Manager") ({g}) site:jobs.lever.co',
    ]

def adjacency_queries(lens):
    g=_geo(lens)
    domains=lens.get("industry_interests",[])
    # Use short, recognisable market terms rather than the full lens prose.
    useful=[x for x in domains if len(x)<28][:8]
    if not useful:
        return []
    first=" OR ".join(f'"{x}"' for x in useful[:4])
    second=" OR ".join(f'"{x}"' for x in useful[4:8])
    qs=[f'"Senior Product Manager" ({g}) ({first})']
    if second:
        qs.append(f'("Senior Product Manager" OR "Staff Product Manager") ({g}) ({second})')
    return qs

def venture_queries(lens):
    g=_geo(lens)
    return [
        f'("Senior Product Manager" OR "Lead Product Manager") ({g}) (startup OR "Series A" OR "Series B" OR "venture-backed")',
        f'("first product manager" OR "founding product manager") ({g})',
    ]

def wildcard_queries(lens):
    g=_geo(lens)
    return [
        f'("Staff Product Manager" OR "Principal Product Manager") ({g}) ("you will own" OR "from concept to launch")',
    ]

def run_scouts(lens,per_query=5,quick=False):
    bundles=[
        ("open market",frontier_queries(lens)),
        ("live ATS",ats_queries(lens)),
        ("adjacent",adjacency_queries(lens)),
        ("startup",venture_queries(lens)),
        ("wildcard",wildcard_queries(lens)),
    ]
    if quick:
        # First-use pass: four compact queries with strong odds of landing on
        # actual role pages. The full pass remains available through “go look”.
        bundles=[
            ("live ATS",ats_queries(lens)[:2]),
            ("open market",frontier_queries(lens)[:1]),
            ("startup",venture_queries(lens)[:1]),
        ]
        per_query=min(per_query,3)

    seen={}
    for scout,queries in bundles:
        for q in queries:
            try:
                results=_search(q,per_query)
            except Exception:
                # One search provider hiccup should not kill the whole pass.
                continue
            for c in results:
                if not c.url:
                    continue
                if c.url in seen:
                    if scout not in seen[c.url].discovery_reason:
                        seen[c.url].discovery_reason += f" · {scout}"
                    continue
                c.discovery_reason=scout
                seen[c.url]=c
    return list(seen.values())
