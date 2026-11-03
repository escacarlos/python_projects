import math
from pathlib import Path
from typing import Any

import pygame

from .components import (
    Animation,
    BoxCollider,
    CameraFollow,
    Health,
    KeyboardControlled,
    Projectile,
    ProjectileEmitter,
    RigidBody,
    Sprite,
    TextLabel,
    Transform,
)
from .ecs import Entity
from .scene import Scene


FPS = 60
BACKGROUND = (21, 21, 21)


class Game:
    def __init__(
        self, scene_path: Path, window_size: tuple[int, int] = (960, 640)
    ) -> None:
        pygame.init()
        pygame.display.set_caption("2D Game Engine - Python")
        self.screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.scene = Scene.load(scene_path)
        self.camera = pygame.Rect(0, 0, *window_size)
        self._sprite_cache: dict[tuple[Any, ...], pygame.Surface] = {}
        self.player_facing = pygame.Vector2(0, -1)
        self.debug = False
        self.running = True
        self.elapsed_ms = 0

    def run(self) -> None:
        while self.running:
            delta_time = min(self.clock.tick(FPS) / 1000.0, 0.1)
            self.elapsed_ms = pygame.time.get_ticks()
            self._process_events()
            if not self.running:
                break
            self._update(delta_time)
            self._render()
        pygame.quit()

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    event.size, pygame.RESIZABLE
                )
                self.camera.size = event.size
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.debug = not self.debug
                elif event.key == pygame.K_SPACE:
                    self._fire_player_projectiles()
                else:
                    self._move_player(event.key)
            elif event.type == pygame.KEYUP:
                self._stop_player(event.key)

    def _move_player(self, key: int) -> None:
        player = self.scene.registry.tagged("player")
        if player is None or not player.has(KeyboardControlled):
            return
        controls = player.get(KeyboardControlled)
        directions = {
            pygame.K_UP: (controls.up, 0),
            pygame.K_RIGHT: (controls.right, 1),
            pygame.K_DOWN: (controls.down, 2),
            pygame.K_LEFT: (controls.left, 3),
        }
        if key not in directions:
            return
        velocity, row = directions[key]
        player.get(RigidBody).velocity = velocity.copy()
        if velocity.length_squared() > 0:
            self.player_facing = velocity.normalize()
        if player.has(Sprite):
            sprite = player.get(Sprite)
            sprite.source_y = row * sprite.height

    def _stop_player(self, key: int) -> None:
        player = self.scene.registry.tagged("player")
        if player is None or not player.has(KeyboardControlled):
            return
        controls = player.get(KeyboardControlled)
        directions = {
            pygame.K_UP: controls.up,
            pygame.K_RIGHT: controls.right,
            pygame.K_DOWN: controls.down,
            pygame.K_LEFT: controls.left,
        }
        direction = directions.get(key)
        if direction is not None and player.get(RigidBody).velocity == direction:
            player.get(RigidBody).velocity.update(0, 0)

    def _fire_player_projectiles(self) -> None:
        player = self.scene.registry.tagged("player")
        if player is None or not player.has(ProjectileEmitter):
            return
        emitter = player.get(ProjectileEmitter)
        velocity = emitter.velocity.copy()
        velocity.x *= self.player_facing.x
        velocity.y *= self.player_facing.y
        self._spawn_projectile(player, velocity)

    def _spawn_projectile(self, owner: Entity, velocity: pygame.Vector2) -> None:
        emitter = owner.get(ProjectileEmitter)
        transform = owner.get(Transform)
        position = transform.position.copy()
        if owner.has(Sprite):
            sprite = owner.get(Sprite)
            position.x += transform.scale.x * sprite.width / 2
            position.y += transform.scale.y * sprite.height / 2
        projectile = self.scene.registry.create(group="projectiles")
        projectile.add(Transform(position))
        projectile.add(RigidBody(velocity.copy()))
        projectile.add(Sprite("bullet-texture", 4, 4, z_index=4))
        projectile.add(BoxCollider(4, 4))
        projectile.add(
            Projectile(
                emitter.friendly,
                emitter.hit_damage,
                emitter.duration,
                pygame.time.get_ticks(),
            )
        )

    def _update(self, delta_time: float) -> None:
        self._update_movement(delta_time)
        self._update_animations()
        self._update_collisions()
        self._update_emitters()
        self._update_projectile_lifetimes()
        self._update_camera()
        self._update_behaviors()
        self.scene.registry.flush()

    def _update_behaviors(self) -> None:
        for entity_id, behavior in list(self.scene.behaviors.items()):
            entity = self.scene.registry.get(entity_id)
            if entity is None:
                continue
            transform = entity.get(Transform)
            rigidbody = entity.get(RigidBody)
            if behavior == "vertical_patrol":
                if transform.position.y < 10 or transform.position.y > self.scene.map_height - 32:
                    rigidbody.velocity.update(0, -rigidbody.velocity.y)
                transform.rotation = 0 if rigidbody.velocity.y < 0 else 180
                if entity.has(ProjectileEmitter):
                    entity.get(ProjectileEmitter).velocity.update(
                        0, -200 if rigidbody.velocity.y < 0 else 200
                    )
            elif behavior == "sine_flight":
                transform.position.update(
                    self.elapsed_ms * 0.09,
                    200 + math.sin(self.elapsed_ms * 0.001) * 50,
                )
            elif behavior == "circular_flight":
                radius = 170
                center = 500
                angle = self.elapsed_ms * 0.0009
                transform.position.update(
                    math.cos(angle) * radius + center,
                    math.sin(angle) * radius + center,
                )
                transform.rotation = 180 + math.degrees(angle)
            else:
                raise ValueError(f"Unknown entity behavior: {behavior!r}")

    def _update_movement(self, delta_time: float) -> None:
        for entity in self.scene.registry.query(Transform, RigidBody):
            transform = entity.get(Transform)
            transform.position += entity.get(RigidBody).velocity * delta_time
            if entity.tag == "player":
                transform.position.x = max(10, min(self.scene.map_width - 50, transform.position.x))
                transform.position.y = max(10, min(self.scene.map_height - 50, transform.position.y))
            elif (
                transform.position.x < -200
                or transform.position.x > self.scene.map_width + 200
                or transform.position.y < -200
                or transform.position.y > self.scene.map_height + 200
            ):
                entity.kill()

    def _update_animations(self) -> None:
        now = pygame.time.get_ticks()
        for entity in self.scene.registry.query(Sprite, Animation):
            sprite = entity.get(Sprite)
            animation = entity.get(Animation)
            frame = ((now - animation.start_time) * animation.speed_rate // 1000) % animation.num_frames
            sprite.source_x = frame * sprite.width

    @staticmethod
    def _overlaps(a: pygame.Rect, b: pygame.Rect) -> bool:
        return a.left < b.right and a.right > b.left and a.top < b.bottom and a.bottom > b.top

    def _collider_rect(self, entity: Entity) -> pygame.Rect:
        transform = entity.get(Transform)
        collider = entity.get(BoxCollider)
        return pygame.Rect(
            int(transform.position.x + collider.offset.x),
            int(transform.position.y + collider.offset.y),
            collider.width,
            collider.height,
        )

    def _update_collisions(self) -> None:
        entities = self.scene.registry.query(Transform, BoxCollider)
        for index, first in enumerate(entities):
            if first.destroyed:
                continue
            first_rect = self._collider_rect(first)
            for second in entities[index + 1 :]:
                if second.destroyed or not self._overlaps(first_rect, self._collider_rect(second)):
                    continue
                self._handle_enemy_obstacle_collision(first, second)
                self._handle_projectile_collision(first, second)

    @staticmethod
    def _handle_enemy_obstacle_collision(first: Entity, second: Entity) -> None:
        pairs = ((first, second), (second, first))
        for enemy, obstacle in pairs:
            if enemy.group == "enemies" and obstacle.group == "obstacles":
                if enemy.has(RigidBody):
                    velocity = enemy.get(RigidBody).velocity
                    if velocity.x:
                        velocity.x *= -1
                    if velocity.y:
                        velocity.y *= -1
                    if enemy.has(Sprite):
                        sprite = enemy.get(Sprite)
                        if velocity.x:
                            sprite.flip_x = not sprite.flip_x
                        if velocity.y:
                            sprite.flip_y = not sprite.flip_y

    def _handle_projectile_collision(self, first: Entity, second: Entity) -> None:
        for projectile_entity, target in ((first, second), (second, first)):
            if projectile_entity.group != "projectiles" or not projectile_entity.has(Projectile):
                continue
            projectile = projectile_entity.get(Projectile)
            valid_target = (
                target.tag == "player" and not projectile.friendly
            ) or (target.group == "enemies" and projectile.friendly)
            if not valid_target or not target.has(Health):
                continue
            health = target.get(Health)
            health.percentage -= projectile.hit_damage
            if health.percentage <= 0:
                target.kill()
            projectile_entity.kill()

    def _update_emitters(self) -> None:
        now = pygame.time.get_ticks()
        for entity in self.scene.registry.query(ProjectileEmitter, Transform):
            emitter = entity.get(ProjectileEmitter)
            if emitter.repeat_frequency <= 0:
                continue
            if (now - emitter.last_emission_time) / 1000.0 > emitter.repeat_frequency:
                self._spawn_projectile(entity, emitter.velocity)
                emitter.last_emission_time = now

    def _update_projectile_lifetimes(self) -> None:
        now = pygame.time.get_ticks()
        for entity in self.scene.registry.query(Projectile):
            projectile = entity.get(Projectile)
            if (now - projectile.start_time) / 1000.0 > projectile.duration:
                entity.kill()

    def _update_camera(self) -> None:
        for entity in self.scene.registry.query(CameraFollow, Transform):
            position = entity.get(Transform).position
            max_x = max(0, self.scene.map_width - self.camera.width)
            max_y = max(0, self.scene.map_height - self.camera.height)
            self.camera.x = round(max(0, min(position.x - self.camera.width / 2, max_x)))
            self.camera.y = round(max(0, min(position.y - self.camera.height / 2, max_y)))

    def _render(self) -> None:
        self.screen.fill(BACKGROUND)
        renderables = self.scene.registry.query(Transform, Sprite)
        renderables.sort(key=lambda entity: entity.get(Sprite).z_index)
        for entity in renderables:
            self._draw_sprite(entity)
        self._draw_health_bars()
        self._draw_text_labels()
        if self.debug:
            self._draw_debug()
        pygame.display.flip()

    def _draw_sprite(self, entity: Entity) -> None:
        transform = entity.get(Transform)
        sprite = entity.get(Sprite)
        source = pygame.Rect(sprite.source_x, sprite.source_y, sprite.width, sprite.height)
        texture = self.scene.assets.texture(sprite.asset_id)
        if not texture.get_rect().contains(source):
            return
        size = (
            max(1, round(sprite.width * transform.scale.x)),
            max(1, round(sprite.height * transform.scale.y)),
        )
        position = transform.position.copy()
        if not sprite.fixed:
            position.x -= self.camera.x
            position.y -= self.camera.y
        if not pygame.Rect(round(position.x), round(position.y), *size).colliderect(
            self.screen.get_rect()
        ):
            return

        cache_key = (
            sprite.asset_id,
            sprite.source_x,
            sprite.source_y,
            sprite.width,
            sprite.height,
            size,
            sprite.flip_x,
            sprite.flip_y,
            transform.rotation,
        )
        image = self._sprite_cache.get(cache_key)
        if image is None:
            image = texture.subsurface(source)
            if image.get_size() != size:
                image = pygame.transform.scale(image, size)
            if sprite.flip_x or sprite.flip_y:
                image = pygame.transform.flip(image, sprite.flip_x, sprite.flip_y)
            if transform.rotation:
                image = pygame.transform.rotate(image, -transform.rotation)
            self._sprite_cache[cache_key] = image

        if transform.rotation:
            center = (round(position.x + size[0] / 2), round(position.y + size[1] / 2))
            self.screen.blit(image, image.get_rect(center=center))
        else:
            self.screen.blit(image, (round(position.x), round(position.y)))

    def _draw_health_bars(self) -> None:
        for entity in self.scene.registry.query(Transform, Sprite, Health):
            transform = entity.get(Transform)
            sprite = entity.get(Sprite)
            health = entity.get(Health).percentage
            x = round(transform.position.x + sprite.width * transform.scale.x - self.camera.x)
            y = round(transform.position.y - self.camera.y)
            if y < -8 or y > self.screen.get_height() or x < 0 or x > self.screen.get_width():
                continue
            color = (255, 0, 0) if health < 40 else (255, 255, 0) if health < 80 else (0, 255, 0)
            pygame.draw.rect(self.screen, color, (x, y, max(0, round(15 * health / 100)), 3))
            if "pico8-font-5" in self.scene.assets.fonts:
                text = self.scene.assets.font("pico8-font-5").render(str(health), True, color)
                self.screen.blit(text, (x, y + 5))

    def _draw_text_labels(self) -> None:
        for entity in self.scene.registry.query(TextLabel):
            label = entity.get(TextLabel)
            position = label.position.copy()
            if not label.fixed:
                position -= self.camera.topleft
            image = self.scene.assets.font(label.asset_id).render(label.text, True, label.color)
            self.screen.blit(image, position)

    def _draw_debug(self) -> None:
        for entity in self.scene.registry.query(Transform, BoxCollider):
            rect = self._collider_rect(entity)
            rect.move_ip(-self.camera.x, -self.camera.y)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 1)
        mouse = pygame.Vector2(pygame.mouse.get_pos()) + self.camera.topleft
        font = pygame.font.Font(None, 20)
        image = font.render(f"Map coordinates (x={mouse.x:.1f}, y={mouse.y:.1f})", True, (255, 255, 255))
        self.screen.blit(image, (10, 10))
