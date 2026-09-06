from scotch.reasoner import assess
from scotch.models import Candidate

def test_ownership_beats_api_only():
    lens={"industry_interests":[],"adjacency_interests":[]}
    a=Candidate("A","Senior Product Manager","https://a","Own the product end-to-end from customer discovery through roadmap launch adoption")
    b=Candidate("B","Senior API Product Manager","https://b","Developer platform infrastructure APIs integration")
    assert assess(a,lens).scotch_score > assess(b,lens).scotch_score
