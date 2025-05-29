from ..ecs import ECSCoordinator
from .. import constants
from ..components.brain_component import BrainComponent, PositionContext, CreatureState
from ..components.energy_component import EnergyComponent
from ..position import Point3D

from random import randint

def updateEvaluations(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        energon: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)

        sleepy = (energon.max - energon.current) / energon.max
        if brain_component.state == CreatureState.AWAKE:
            pos = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            for evaluator in brain_component.evaluators:
                constants.evaluator_types[evaluator.evaluator_id](coordinator, entity_id, brain_component, evaluator.data)

            if sleepy > 0.9:
                brain_component.state = CreatureState.SLEEPING
                brain_component.target_creature.valid = False
                brain_component.target_position.valid = False
            elif brain_component.must_roam:
                brain_component.target_creature.valid = False
                brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
            elif len(brain_component.entities) > 0:
                sortation = sorted(brain_component.entities, key=lambda x: x.nutritionByDistance(pos) - x.threatByDistance(pos), reverse=True)[0]
                if sortation.nutrition > 0:
                    brain_component.target_creature.setCreature(sortation.id)
                    brain_component.target_position.setPosition(coordinator.getComponent(sortation.id, constants.POSITION_COMPONENT), PositionContext.FOOD)
                else:
                    brain_component.target_creature.valid = False
                    brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
            else:
                brain_component.target_creature.valid = False
                brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
        elif brain_component.state == CreatureState.SLEEPING:
            if sleepy < 0.1:
                brain_component.state = CreatureState.AWAKE
