from dataclasses import dataclass
from typing import Any

@dataclass
class TimerComponent:
    current: int
    time: int
    remove: list[str]
    add: list[tuple[str, Any]]