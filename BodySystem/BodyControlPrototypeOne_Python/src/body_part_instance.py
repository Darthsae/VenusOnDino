from .body_part_type import BodyPartType
from .physics.connection import Connection

class BodyPartInstance:
    def __init__(self, type: BodyPartType, name: str):
        self.type = type
        self.name = name
        self.connections: Connection