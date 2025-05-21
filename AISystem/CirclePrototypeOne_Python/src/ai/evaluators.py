from .evaluator import IEvaluator, ECSCoordinator, entity, Any
from ..components.brain_component import BrainComponent, PositionContext
from .. import constants
from ..position import Point3D

class TargetEvaluator(IEvaluator):
    def evaluate(self, coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
        brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if len(brain.entities) > 0:
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            closest_point = sorted(brain.entities, key = lambda tup: position.distSQ(tup[0]))[0][0]
            brain.target_position.setPosition(closest_point, PositionContext.ROAM)
