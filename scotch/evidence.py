import re, requests
from bs4 import BeautifulSoup
from .models import Candidate
from .signals import infer_domain
HEADERS={"User-Agent":"Mozilla/5.0 ScotchResearch/2.0"}

def enrich(c: Candidate) -> Candidate:
    try:
        r=requests.get(c.url,headers=HEADERS,timeout=10,allow_redirects=True)
        if r.ok and "text" in r.headers.get("content-type",""):
            soup=BeautifulSoup(r.text,"html.parser")
            for x in soup(["script","style","noscript"]): x.decompose()
            c.page_text=" ".join(soup.stripped_strings)[:50000]
    except Exception: pass
    blob=c.page_text or c.snippet
    c.location=_extract_location(blob); c.compensation=_extract_comp(blob); c.domain=infer_domain(blob); c.role=_clean_title(c.role); c.company=_company_guess(c); c.posted_hint=_posted_hint(blob)
    return c

def _extract_location(t):
    m=re.search(r'\b(Toronto|Greater Toronto Area|GTA|Ontario|Canada|Montreal|Vancouver|Remote)\b[^.;]{0,65}',t,re.I)
    return m.group(0)[:80] if m else ""
def _extract_comp(t):
    m=re.search(r'(?:CA\$|CAD\s*\$?|\$)\s?\d{2,3}(?:[,\d]{0,4})\s?[Kk]?(?:\s*(?:–|-|to)\s*(?:CA\$|CAD\s*\$?|\$)?\s?\d{2,3}(?:[,\d]{0,4})\s?[Kk]?)?',t)
    return m.group(0) if m else ""
def _posted_hint(t):
    m=re.search(r'(?:posted|updated)\s+(?:on\s+)?([A-Z][a-z]{2,8}\s+\d{1,2},?\s+\d{4}|\d+\s+(?:day|days|week|weeks)\s+ago)',t,re.I)
    return m.group(0) if m else ""
def _clean_title(t): return re.sub(r'\s+',' ',t).strip()[:170]
def _company_guess(c):
    parts=[p.strip() for p in re.split(r'\s+[|–—-]\s+',c.role) if p.strip()]; pm=[i for i,p in enumerate(parts) if "product manager" in p.lower()]
    if pm and len(parts)>1:
        others=[p for i,p in enumerate(parts) if i!=pm[0]]
        if others and 2<=len(others[0])<=70:
            c.role=parts[pm[0]]; return others[0]
    return c.company
