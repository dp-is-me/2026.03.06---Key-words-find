from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Suggestion:
    toolset: str
    summary: str
    next_steps: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Attempt:
    timestamp: datetime
    action: str
    result: str
