from ..ecs import ECSCoordinator
from .. import constants
from ..components.brain_component import BrainComponent
from ..world.terrain import Terrain

def updateEvaluations(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        for evaluator in brain_component.evaluators:
            constants.evaluator_types[evaluator.evaluator_id](coordinator, entity_id, terrain, evaluator.data)
                
