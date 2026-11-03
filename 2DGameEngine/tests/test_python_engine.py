import json
import os
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from python_engine.components import (
    BoxCollider,
    Health,
    ProjectileEmitter,
    Projectile,
    RigidBody,
    Sprite,
    Transform,
)
from python_engine.engine import Game
from python_engine.scene import Scene


ROOT = Path(__file__).resolve().parents[1]
SCENE_PATH = ROOT / "assets/levels/level1.json"


class PythonEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(SCENE_PATH, (640, 480))

    def tearDown(self) -> None:
        pygame.quit()

    def test_loads_complete_json_level_and_assets(self) -> None:
        scene_data = json.loads(SCENE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(scene_data["tilemap"]["tiles"]), 20)
        self.assertTrue(all(len(row) == 25 for row in scene_data["tilemap"]["tiles"]))
        self.assertEqual(len(self.game.scene.registry.query(Transform, Sprite)), 619)
        self.assertEqual(len(self.game.scene.behaviors), 2)
        self.assertTrue(
            all(
                entity.get(Sprite).asset_id in self.game.scene.assets.textures
                for entity in self.game.scene.registry.query(Sprite)
            )
        )
        randomized_emitter = next(
            entity
            for entity in self.game.scene.registry.query(Transform, ProjectileEmitter)
            if entity.get(Transform).position == pygame.Vector2(200, 497)
        )
        self.assertIn(
            randomized_emitter.get(ProjectileEmitter).velocity.x, range(10, 201)
        )

    def test_player_input_projectiles_and_frame_rendering(self) -> None:
        player = self.game.scene.registry.tagged("player")
        self.assertIsNotNone(player)
        assert player is not None
        self.game._move_player(pygame.K_RIGHT)
        self.assertEqual(player.get(RigidBody).velocity, pygame.Vector2(50, 0))
        self.game._stop_player(pygame.K_RIGHT)
        self.game._fire_player_projectiles()
        bullets = [
            entity
            for entity in self.game.scene.registry.query(Sprite)
            if entity.group == "projectiles"
        ]
        self.assertEqual(len(bullets), 1)
        self.assertEqual(bullets[0].get(Sprite).asset_id, "bullet-texture")
        self.assertEqual(bullets[0].get(RigidBody).velocity, pygame.Vector2(200, 0))
        self.assertEqual(player.get(RigidBody).velocity, pygame.Vector2(0, 0))
        self.game._update(1 / 60)
        self.game._render()
        self.assertTrue(self.game._sprite_cache)

    def test_stationary_player_fires_in_last_facing_direction(self) -> None:
        self.game._fire_player_projectiles()
        bullet = next(
            entity
            for entity in self.game.scene.registry.query(Sprite)
            if entity.group == "projectiles"
        )
        self.assertEqual(bullet.get(RigidBody).velocity, pygame.Vector2(0, -200))

    def test_level2_json_loads_and_preserves_its_behaviors(self) -> None:
        scene_path = ROOT / "assets/levels/level2.json"
        scene = Scene.load(scene_path)
        self.assertEqual(scene.map_width, 2560)
        self.assertEqual(scene.map_height, 1920)
        self.assertEqual(len(scene.registry.query(Transform, Sprite)), 1306)
        self.assertEqual(
            set(scene.behaviors.values()), {"vertical_patrol", "circular_flight"}
        )
        self.assertTrue(
            all(
                entity.get(Sprite).asset_id in scene.assets.textures
                for entity in scene.registry.query(Sprite)
            )
        )

    def test_level2_circular_flight_behavior(self) -> None:
        game = Game(ROOT / "assets/levels/level2.json", (640, 480))
        entity_id = next(
            entity_id
            for entity_id, behavior in game.scene.behaviors.items()
            if behavior == "circular_flight"
        )
        game.elapsed_ms = 0
        game._update_behaviors()
        entity = game.scene.registry.get(entity_id)
        self.assertIsNotNone(entity)
        assert entity is not None
        self.assertEqual(entity.get(Transform).position, pygame.Vector2(670, 500))
        self.assertEqual(entity.get(Transform).rotation, 180)

    def test_friendly_projectile_damages_an_enemy(self) -> None:
        enemy = self.game.scene.registry.create(group="enemies")
        enemy.add(Transform(pygame.Vector2(1500, 1200)))
        enemy.add(BoxCollider(8, 8))
        enemy.add(Health(100))
        projectile = self.game.scene.registry.create(group="projectiles")
        projectile.add(Transform(pygame.Vector2(1500, 1200)))
        projectile.add(BoxCollider(4, 4))
        projectile.add(Projectile(True, 30, 2, pygame.time.get_ticks()))

        self.game._update_collisions()

        self.assertEqual(enemy.get(Health).percentage, 70)
        self.assertTrue(projectile.destroyed)


if __name__ == "__main__":
    unittest.main()
