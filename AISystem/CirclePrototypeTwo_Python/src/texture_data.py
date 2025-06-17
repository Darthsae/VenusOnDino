from dataclasses import dataclass
import pygame
from pygame import Surface, Rect

@dataclass
class TextureData:
    texture: Surface
    rect: Rect

    @classmethod
    def load(cls, filepath):
        surface: Surface = pygame.image.load(filepath)
        rect: Rect = surface.get_rect()
        return cls(surface, rect)