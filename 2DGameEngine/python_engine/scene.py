import json
import random
from pathlib import Path
from typing import Any

import pygame

from .components import (
    Animation,
    BoxCollider,
    CameraFollow,
    Health,
    KeyboardControlled,
    ProjectileEmitter,
    RigidBody,
    Sprite,
    TextLabel,
    Transform,
)
from .ecs import Entity, Registry


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _vector(
    value: dict[str, Any] | None, default: tuple[float, float] = (0, 0)
) -> pygame.Vector2:
    if value is None:
        return pygame.Vector2(default)
    coordinates = []
    for axis, fallback in zip(("x", "y"), default):
        coordinate = value.get(axis, fallback)
        if isinstance(coordinate, dict):
            low, high = coordinate["random"]
            coordinate = random.randint(int(low), int(high))
        coordinates.append(coordinate)
    return pygame.Vector2(coordinates)


class AssetStore:
    def __init__(self) -> None:
        self.textures: dict[str, pygame.Surface] = {}
        self.fonts: dict[str, pygame.font.Font] = {}

    def load(self, definitions: list[dict[str, Any]]) -> None:
        for definition in definitions:
            asset_id = definition["id"]
            asset_path = (PROJECT_ROOT / definition["file"]).resolve()
            if not asset_path.is_file():
                raise FileNotFoundError(f"Asset {asset_id!r} not found: {asset_path}")
            if definition["type"] == "texture":
                self.textures[asset_id] = pygame.image.load(asset_path).convert_alpha()
            elif definition["type"] == "font":
                self.fonts[asset_id] = pygame.font.Font(
                    str(asset_path), int(definition["font_size"])
                )
            else:
                raise ValueError(f"Unsupported asset type: {definition['type']!r}")

    def texture(self, asset_id: str) -> pygame.Surface:
        try:
            return self.textures[asset_id]
        except KeyError as error:
            raise KeyError(f"Texture asset {asset_id!r} was not loaded") from error

    def font(self, asset_id: str) -> pygame.font.Font:
        try:
            return self.fonts[asset_id]
        except KeyError as error:
            raise KeyError(f"Font asset {asset_id!r} was not loaded") from error


class Scene:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.registry = Registry()
        self.assets = AssetStore()
        self.map_width = 0
        self.map_height = 0
        self.map_scale = 1.0
        self.behaviors: dict[int, str] = {}

    @classmethod
    def load(cls, scene_path: Path) -> "Scene":
        with scene_path.open(encoding="utf-8") as scene_file:
            data = json.load(scene_file)
        scene = cls(data)
        scene.assets.load(data["assets"])
        scene._load_tilemap(data["tilemap"])
        for entity_data in data["entities"]:
            entity = scene.registry.create(
                tag=entity_data.get("tag"), group=entity_data.get("group")
            )
            scene._add_components(entity, entity_data.get("components", {}))
            if behavior := entity_data.get("behavior"):
                scene.behaviors[entity.id] = behavior
        return scene

    def _load_tilemap(self, tilemap: dict[str, Any]) -> None:
        rows = tilemap["tiles"]
        if not rows or not rows[0]:
            raise ValueError("Tilemap must contain at least one tile")
        num_rows = len(rows)
        num_cols = len(rows[0])
        tile_size = int(tilemap["tile_size"])
        self.map_scale = float(tilemap.get("scale", 1.0))
        if any(len(row) != num_cols for row in rows):
            raise ValueError(
                f"Tilemap rows must contain the same number of tiles ({num_cols})"
            )

        for row_index, row in enumerate(rows):
            for col_index in range(num_cols):
                tile_index = row[col_index]
                if len(tile_index) != 2:
                    raise ValueError(
                        f"Invalid tile index {tile_index!r} at ({col_index}, {row_index})"
                    )
                try:
                    source_y, source_x = (int(value) for value in tile_index)
                except ValueError as error:
                    raise ValueError(
                        f"Invalid tile index {tile_index!r} at ({col_index}, {row_index})"
                    ) from error
                entity = self.registry.create()
                entity.add(
                    Transform(
                        pygame.Vector2(
                            col_index * tile_size * self.map_scale,
                            row_index * tile_size * self.map_scale,
                        ),
                        pygame.Vector2(self.map_scale, self.map_scale),
                    )
                )
                entity.add(
                    Sprite(
                        tilemap["texture_asset_id"],
                        tile_size,
                        tile_size,
                        source_x=source_x * tile_size,
                        source_y=source_y * tile_size,
                    )
                )

        self.map_width = int(num_cols * tile_size * self.map_scale)
        self.map_height = int(num_rows * tile_size * self.map_scale)

    def _add_components(self, entity: Entity, components: dict[str, Any]) -> None:
        if "transform" in components:
            value = components["transform"]
            entity.add(
                Transform(
                    _vector(value.get("position")),
                    _vector(value.get("scale"), (1, 1)),
                    float(value.get("rotation", 0)),
                )
            )
        if "rigidbody" in components:
            entity.add(RigidBody(_vector(components["rigidbody"].get("velocity"))))
        if "sprite" in components:
            value = components["sprite"]
            entity.add(
                Sprite(
                    value["texture_asset_id"],
                    int(value["width"]),
                    int(value["height"]),
                    int(value.get("z_index", 0)),
                    bool(value.get("fixed", False)),
                    int(value.get("src_rect_x", 0)),
                    int(value.get("src_rect_y", 0)),
                )
            )
        if "animation" in components:
            value = components["animation"]
            entity.add(
                Animation(
                    int(value.get("num_frames", 1)),
                    int(value.get("speed_rate", 1)),
                    pygame.time.get_ticks(),
                )
            )
        if "boxcollider" in components:
            value = components["boxcollider"]
            entity.add(
                BoxCollider(
                    int(value["width"]),
                    int(value["height"]),
                    _vector(value.get("offset")),
                )
            )
        if "health" in components:
            entity.add(
                Health(int(components["health"].get("health_percentage", 100)))
            )
        if "projectile_emitter" in components:
            value = components["projectile_emitter"]
            entity.add(
                ProjectileEmitter(
                    _vector(value.get("projectile_velocity")),
                    float(value.get("repeat_frequency", 0)),
                    float(value.get("projectile_duration", 10)),
                    int(value.get("hit_percentage_damage", 10)),
                    bool(value.get("friendly", False)),
                    pygame.time.get_ticks(),
                )
            )
        if "keyboard_controller" in components:
            value = components["keyboard_controller"]
            entity.add(
                KeyboardControlled(
                    _vector(value.get("up_velocity")),
                    _vector(value.get("right_velocity")),
                    _vector(value.get("down_velocity")),
                    _vector(value.get("left_velocity")),
                )
            )
        if "camera_follow" in components:
            entity.add(CameraFollow())
        if "text_label" in components:
            value = components["text_label"]
            entity.add(
                TextLabel(
                    _vector(value.get("position")),
                    str(value.get("text", "")),
                    value["asset_id"],
                    tuple(value.get("color", (0, 0, 0))),
                    bool(value.get("fixed", True)),
                )
            )
