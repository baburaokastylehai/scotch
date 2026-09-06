from dataclasses import dataclass, asdict

@dataclass
class Candidate:
    company: str
    role: str
    url: str
    snippet: str = ""
    source: str = ""
    discovery_reason: str = ""
    location: str = ""
    compensation: str = ""
    domain: str = ""
    page_text: str = ""

@dataclass
class Assessment:
    ownership: int
    transfer: int
    step_up: int
    optionality: int
    venture_upside: int
    risk: int
    scotch_score: int
    interpretation: str
    critique: str
    recommendation: str

    def asdict(self):
        return asdict(self)
