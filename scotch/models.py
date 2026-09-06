from dataclasses import dataclass, asdict, field

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
    posted_hint: str = ""

@dataclass
class Assessment:
    ownership: int
    transfer: int
    step_up: int
    optionality: int
    venture_upside: int
    risk: int
    signal: int
    why_this: str
    what_you_own: str
    what_carries: str
    stretch: str
    critique: str
    recommendation: str
    evidence: list[str] = field(default_factory=list)

    def asdict(self): return asdict(self)
