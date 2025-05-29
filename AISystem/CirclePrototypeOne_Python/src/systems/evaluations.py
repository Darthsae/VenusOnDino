from ..ecs import ECSCoordinator
from .. import constants
from ..components.brain_component import BrainComponent, PositionContext, CreatureState, Emoticon
from ..components.energy_component import EnergyComponent
from ..world.terrain import Terrain
from ..position import Point3D

from random import randint

def updateEvaluations(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        brain_component.emoticon = Emoticon.NONE
        if brain_component.state == CreatureState.AWAKE:
            pos = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            for evaluator in brain_component.evaluators:
                constants.evaluator_types[evaluator.evaluator_id](coordinator, entity_id, terrain, evaluator.data)

            energon: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)

            sleepy = (energon.max - energon.current) / energon.max

            if sleepy > 0.9:
                brain_component.state = CreatureState.SLEEPING
                brain_component.target_creature.valid = False
                brain_component.target_position.valid = False
            elif len(brain_component.entities) > 0:
                #for wacko in brain_component.entities:
                    #print(f"{wacko.nutritionByDistance(pos)} - {wacko.threatByDistance(pos)} = {wacko.nutritionByDistance(pos) - wacko.threatByDistance(pos)}")
                sortation = sorted(brain_component.entities, key=lambda x: x.nutritionByDistance(pos) - x.threatByDistance(pos), reverse=True)[0]
                if sortation.nutrition > 0:
                    #print(sortation.nutrition)
                    brain_component.target_creature.setCreature(sortation.id)
                    brain_component.target_position.setPosition(coordinator.getComponent(sortation.id, constants.POSITION_COMPONENT), PositionContext.ROAM)
                else:
                    brain_component.target_creature.valid = False
                    brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
            else:
                brain_component.target_creature.valid = False
                brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
        elif brain_component.state == CreatureState.SLEEPING:
            energon: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)

            sleepy = (energon.max - energon.current) / energon.max

            if sleepy < 0.1:
                brain_component.state = CreatureState.AWAKE
