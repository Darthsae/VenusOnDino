from .body_part_type import BodyPartType

class BodyPartInstance:
    def __init__(self, type: BodyPartType):
        self.type = type