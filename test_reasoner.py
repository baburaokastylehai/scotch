from scotch.reasoner import assess
from scotch.models import Candidate
LENS={"industry_interests":["B2B SaaS","Fintech","Travel & Hospitality"],"adjacency_interests":["PLM","QMS","Supply Chain"],"desired_ownership":["own a product end-to-end"]}
def test_ownership_beats_platform_only():
    good=Candidate("A","Senior Product Manager","https://a",snippet="Own the product end-to-end from customer discovery through product strategy, roadmap, launch, adoption and iteration.")
    platform=Candidate("B","Senior Product Manager, Developer Platform","https://b",snippet="Own developer platform infrastructure, APIs and platform enablement.")
    assert assess(good,LENS).signal > assess(platform,LENS).signal
def test_startup_signal_increases_upside():
    startup=Candidate("A","Senior Product Manager","https://a",snippet="Series B startup. Equity. Work with founders. First PM for a new product line. Own roadmap and launch.")
    plain=Candidate("B","Senior Product Manager","https://b",snippet="Support roadmap delivery with engineering.")
    assert assess(startup,LENS).venture_upside > assess(plain,LENS).venture_upside
