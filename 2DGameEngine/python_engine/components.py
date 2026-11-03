from dataclasses import dataclass, field

import pygame


@dataclass
class Transform:
    position: pygame.Vector2
    scale: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(1, 1))
    rotation: float = 0


@dataclass
class RigidBody:
    velocity: pygame.Vector2 = field(default_factory=pygame.Vector2)


@dataclass
class Sprite:
    asset_id: str
    width: int
    height: int
    z_index: int = 0
    fixed: bool = False
    source_x: int = 0
    source_y: int = 0
    flip_x: bool = False
    flip_y: bool = False


@dataclass
class Animation:
    num_frames: int = 1
    speed_rate: int = 1
    start_time: int = 0


@dataclass
class BoxCollider:
    width: int
    height: int
    offset: pygame.Vector2 = field(default_factory=pygame.Vector2)


@dataclass
class Health:
    percentage: int = 100


@dataclass
class ProjectileEmitter:
    velocity: pygame.Vector2
    repeat_frequency: float
    duration: float
    hit_damage: int
    friendly: bool
    last_emission_time: int = 0


@dataclass
class Projectile:
    friendly: bool
    hit_damage: int
    duration: float
    start_time: int


@dataclass
class KeyboardControlled:
    up: pygame.Vector2
    right: pygame.Vector2
    down: pygame.Vector2
    left: pygame.Vector2


@dataclass
class CameraFollow:
    pass


@dataclass
class TextLabel:
    position: pygame.Vector2
    text: str
    asset_id: str
    color: tuple[int, int, int] = (0, 0, 0)
    fixed: bool = True
