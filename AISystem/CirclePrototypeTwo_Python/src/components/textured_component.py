from dataclasses import dataclass

@dataclass
class TexturedComponent:
    texture_id: int
    draw_centered: bool = True