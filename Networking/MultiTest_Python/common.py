import pygame, numpy, socket, select, math
from dataclasses import dataclass
from pygame import Vector2

PLAYER_HEALTH: int = 100
PLAYER_SIZE: float = 8
CELL_SIZE: float = 16

SERVER_IP: str = "127.0.0.1"
PORT: int = 12345
BUFFER_SIZE: int = 1024

class Map:
    def __init__(self, data: dict[str]):
        self.grid = numpy.zeros((36, 36))

    def cast(self, position: Vector2, move: Vector2):
        rec = 0
        pos = position
        while rec < 250:
            pos = self.nextVoxel(pos, move)
            if pos == -1:
                return 0, position + move * 8
            if self.isSolid(pos):
                return 1, pos
            rec += 1
        return 0, pos
            
    def isSolid(self, position: Vector2):
        return self.voxel(position) != -1

    def voxel(self, position: Vector2):
        nextVX =  math.floor(position.x // 16)
        nextVY =  math.floor(position.y // 16)

        if not (0 < nextVX < self.size):
            return -1

        if not (0 < nextVY < self.size):
            return -1
        
        return self.grid[nextVY][nextVX]

    def nextVoxel(self, position: Vector2, move: Vector2):
        tMaxX = 0
        tMaxY = 0
        X = math.copysign(1, move.x)
        Y = math.copysign(1, move.y)
        vX = math.floor(position.x // 16)
        vY = math.floor(position.y // 16)
        nextVX = vX + X
        nextVY = vY + Y

        if not (0 < nextVX < self.size):
            return -1

        if not (0 < nextVY < self.size):
            return -1
        
        nextX = vX * 16 - 1 if X < 0 else nextVX * 16
        nextY = vY * 16 - 1 if Y < 0 else nextVY * 16

        dX = nextX - position.x
        dY = nextY - position.y

        tMaxX = dX / move.x if move.x != 0 else 999
        tMaxY = dY / move.y if move.y != 0 else 999


        return position + move * min(tMaxX, tMaxY)

class Entity:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.hp = 100
    
    def __str__(self):
        return f"{self.x},{self.y},{self.hp}"