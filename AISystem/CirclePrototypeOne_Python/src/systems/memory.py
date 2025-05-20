from ..ecs import ECSCoordinator
from .. import constants
from ..components.memory_component import MemoryComponent

def workingMemory(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.WORKING_MEMORY_COMPONENT):
        working_memory: MemoryComponent = coordinator.getComponent(entity_id, constants.WORKING_MEMORY_COMPONENT)

def assosciativeMemory(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ASSOSCIATIVE_MEMORY_COMPONENT):
        assosciative_memory: MemoryComponent = coordinator.getComponent(entity_id, constants.ASSOSCIATIVE_MEMORY_COMPONENT)
        