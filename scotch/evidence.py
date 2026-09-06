import re, requests
from bs4 import BeautifulSoup
from .models import Candidate

HEADERS={"User-Agent":"Mozilla/5.0 ScotchResearch/1.0"}

def enrich(c: Candidate) -> Candidate:
    try:
        r=requests.get(c.url,headers=HEADERS,timeout=10)
        if r.ok and "text" in r.headers.get("content-type",""):
            soup=BeautifulSoup(r.text,"html.parser")
            for x in soup(["script","style","noscript"]): x.decompose()
            c.page_text=" ".join(soup.stripped_strings)[:40000]
    except Exception: pass
    blob=(c.page_text or c.snippet)
    c.location=_extract_location(blob); c.compensation=_extract_comp(blob); c.domain=_domain(blob); c.role=_clean_title(c.role)
    return c

def _extract_location(t):
    m=re.search(r'\b(Toronto|Ontario|Canada|Montreal|Vancouver|Remote)\b[^.;]{0,55}',t,re.I)
    return m.group(0)[:70] if m else ""

def _extract_comp(t):
    m=re.search(r'(?:CA\$|CAD\s*\$?|\$)\s?\d{2,3}(?:[,\d]{0,4})\s?[Kk]?(?:\s*(?:–|-|to)\s*(?:CA\$|CAD\s*\$?|\$)?\s?\d{2,3}(?:[,\d]{0,4})\s?[Kk]?)?',t)
    return m.group(0) if m else ""

def _domain(t):
    x=t.lower(); maps=[("Travel & Hospitality",["hospitality","travel","hotel","restaurant","booking","guest","tour"]),("Fintech",["fintech","payments","banking","wealth","lending","mortgage","financial services"]),("Industrial / PLM",["plm","product lifecycle","manufacturing","qms","quality management","bom","supply chain","lims"]),("AI",["agentic","generative ai","artificial intelligence","llm","machine learning"]),("B2B SaaS",["b2b","saas","enterprise software"])]
    for label,terms in maps:
        if any(k in x for k in terms): return label
    return "Other"

def _clean_title(t): return re.sub(r'\s+',' ',t).strip()[:150]
