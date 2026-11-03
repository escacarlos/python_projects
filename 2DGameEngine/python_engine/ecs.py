from collections.abc import Iterator
from typing import TypeVar, cast


Component = TypeVar("Component")


class Entity:
    def __init__(self, entity_id: int, registry: "Registry") -> None:
        self.id = entity_id
        self.registry = registry
        self.components: dict[type, object] = {}
        self.tag: str | None = None
        self.group: str | None = None
        self.destroyed = False

    def add(self, component: Component) -> Component:
        self.components[type(component)] = component
        return component

    def get(self, component_type: type[Component]) -> Component:
        try:
            return cast(Component, self.components[component_type])
        except KeyError as error:
            raise KeyError(
                f"Entity {self.id} has no {component_type.__name__} component"
            ) from error

    def has(self, component_type: type) -> bool:
        return component_type in self.components

    def kill(self) -> None:
        self.destroyed = True


class Registry:
    def __init__(self) -> None:
        self._next_id = 0
        self._entities: dict[int, Entity] = {}

    def create(self, tag: str | None = None, group: str | None = None) -> Entity:
        entity = Entity(self._next_id, self)
        self._next_id += 1
        entity.tag = tag
        entity.group = group
        self._entities[entity.id] = entity
        return entity

    def entities(self) -> Iterator[Entity]:
        return (entity for entity in self._entities.values() if not entity.destroyed)

    def query(self, *component_types: type) -> list[Entity]:
        return [
            entity
            for entity in self.entities()
            if all(entity.has(component_type) for component_type in component_types)
        ]

    def tagged(self, tag: str) -> Entity | None:
        return next((entity for entity in self.entities() if entity.tag == tag), None)

    def get(self, entity_id: int) -> Entity | None:
        entity = self._entities.get(entity_id)
        return entity if entity is not None and not entity.destroyed else None

    def flush(self) -> None:
        for entity_id in [
            entity_id for entity_id, entity in self._entities.items() if entity.destroyed
        ]:
            del self._entities[entity_id]
