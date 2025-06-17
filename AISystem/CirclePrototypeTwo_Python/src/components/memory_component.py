from dataclasses import dataclass
from typing import Any
from enum import Enum

class MemoryType(Enum):
    ACTIVE_TARGET = 0
    ACTIVE_ALLY = 1
    MATE = 2
    CLOSE_RELATION = 3
    CORPSE = 4
    PAST_THREAT = 5

@dataclass
class MemorySlot:
    memory_type: MemoryType
    memory_data: Any
    memory_decay: int

@dataclass
class MemoryComponent:
    slots: set[MemorySlot]