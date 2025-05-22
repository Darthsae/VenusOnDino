from typing import TypeAlias, Any
from ctypes import c_uint64

entity: TypeAlias = int
component: TypeAlias = int

class ECSCoordinator:
    def __init__(self):
        self.entities: dict[entity, set[component]] = {}
        self.__components: dict[component, dict[entity, Any]] = {}
        self.__next_entity_id: int = 0
        self.__next_component_id: int = 0
    
    def createEntity(self) -> entity:
        entity_id: entity = entity(self.__next_entity_id)
        self.entities[entity_id] = set()
        while entity(self.__next_entity_id) in self.entities:
            self.__next_entity_id += 1
        return entity_id
    
    def removeEntity(self, entity_id: entity):
        components: set[component] = self.entities.pop(entity_id)
        for component_id in components:
            self.__components[component_id].pop(entity_id)
        if entity_id < self.__next_entity_id:
            self.__next_entity_id = entity_id

    def registerComponent(self) -> component:
        component_id: component = component(self.__next_component_id)
        self.__components[component_id] = {}
        while component(self.__next_component_id) in self.__components:
            self.__next_component_id += 1
        return component_id
    
    def setComponent[T](self, entity_id: entity, component_id: component, data: T):
        self.__components[component_id][entity_id] = data
        self.entities[entity_id] |= {component_id}

    def removeComponents(self, entity_id: entity, components: set[component]):
        self.entities[entity_id] -= components
        for component in components:
            #print(component)
            self.__components[component].pop(entity_id)

    def hasComponent(self, entity_id: entity, component_id: component) -> bool:
        return component_id in self.entities[entity_id]

    def getComponent[T](self, entity_id: entity, component_id: component) -> T:
        return self.__components[component_id][entity_id]

    def getEntitiesWithComponent(self, component_id: component) -> set[entity]:
        return set(self.__components[component_id].keys())
