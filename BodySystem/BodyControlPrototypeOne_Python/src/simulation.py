from dataclasses import dataclass
from typing import Callable, TypeAlias, Any

Function: TypeAlias = Callable[["Simulation"], None]
FunctionWithInput: TypeAlias = Callable[["Simulation", str], None]

@dataclass
class Simulation:
    start: Function
    update: Function
    display: Function
    input: FunctionWithInput
    data: dict[str, Any]