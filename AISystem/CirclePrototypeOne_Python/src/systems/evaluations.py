from ..ecs import ECSCoordinator, entity
from .. import constants
from ..components.brain_component import BrainComponent, PositionContext, CreatureState, CreatureContext
from ..components.energy_component import EnergyComponent
from ..components.physical_body import PhysicalBody
from ..components.diet_component import DietComponent
from ..position import Point3D
from ..ai import goal

from random import randint

def evaluate(coordinator: ECSCoordinator, entity_id: entity, brain_component: BrainComponent, data: dict[str]):
    larger: float = data["larger"]
    smaller: float = data["smaller"]
    damage: float = data["damage"]
    low_health: float = data["low_health"]
    nutrition: float = data["nutrition"]
    size: float = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT).size
    
    for entity_iter in brain_component.entities:
        entity_iter.nutrition = nutrition * 1
        entity_size: float = coordinator.getComponent(entity_iter, constants.PHYSICAL_BODY_COMPONENT).size
        
        entity_iter.threat = larger * (entity_size - size) + smaller * (size - entity_size)

def updateEvaluations(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        energon: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)

        goals: list[goal.Goal] = []

        evaluate(coordinator, entity_id, brain_component, {
            "larger": 1,
            "smaller": 1,
            "damage": 1,
            "low_health": 1,
            "nutrition": 1
        })

        goals.append(goal.SleepGoal(energon))
        goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {})
        goals.append(goal.RoamGoal())
        goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {})
        goals.append(goal.ScavengeGoal())
        goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {"full_health": 1, "low_health": 1})
        goals.append(goal.HuntGoal())
        goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {"full_health": 1, "low_health": 1})
        diet_component: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
        for butrient in diet_component.nutrients:
            goals.append(goal.NutritionGoal(butrient))
            goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {})
        if brain_component.attacker in coordinator.entities:
            goals.append(goal.DefendGoal(brain_component.attacker))
            goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {"full_health": 1, "low_health": 1})
            goals.append(goal.FleeGoal(brain_component.attacker))
            goals[-1].value, goals[-1].rank = goals[-1].evaluate(coordinator, None, entity_id, brain_component, {"full_health": 1, "low_health": 1})
        goals.sort(key = lambda moo: moo.value)
        goals.sort(key = lambda moo: moo.rank)

        #goals.reverse()

        pass
        

def updateEvaluationsOld(coordinator: ECSCoordinator):
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
            elif brain_component.attacker != -1:
                if brain_component.attacker in coordinator.entities and coordinator.hasComponent(brain_component.attacker, constants.HEALTH_COMPONENT):
                    if coordinator.hasComponent(entity_id, constants.ATTACK_TARGET_COMPONENT):
                        #print(f"{entity_id} is defending against {sortation.id}")
                        brain_component.target_creature.setCreature(brain_component.attacker, CreatureContext.FIGHT)
                        brain_component.target_position.setPosition(coordinator.getComponent(brain_component.attacker, constants.POSITION_COMPONENT), PositionContext.FIGHT)
                    else:
                        #print(f"{entity_id} is fleeing from {sortation.id}")
                        direction: Point3D = pos - coordinator.getComponent(brain_component.attacker, constants.POSITION_COMPONENT)
                        brain_component.target_creature.valid = False
                        brain_component.target_position.setPosition(pos - Point3D(direction.x, direction.y, 0), PositionContext.SAFETY)
                else:
                    #print(f"{entity_id} has invalid attacker")
                    brain_component.attacker = -1
            elif len(brain_component.entities) > 0:
                sortation = sorted(brain_component.entities, key=lambda x: x.nutritionByDistance(pos) - x.threatByDistance(pos), reverse=True)[0]
                if sortation.nutrition != None and sortation.nutrition > 0:
                    #print(f"Nutrition -> {sortation.id}")
                    if sortation.threat == None:
                        #print(f"{entity_id} is eating {sortation.id}")
                        brain_component.target_creature.setCreature(sortation.id, CreatureContext.EAT)
                        brain_component.target_position.setPosition(coordinator.getComponent(sortation.id, constants.POSITION_COMPONENT), PositionContext.FOOD)
                    else:
                        #print(f"{entity_id} is fighting {sortation.id}")
                        brain_component.target_creature.setCreature(sortation.id, CreatureContext.FIGHT)
                        brain_component.target_position.setPosition(coordinator.getComponent(sortation.id, constants.POSITION_COMPONENT), PositionContext.FIGHT)
                elif sortation.threatByDistance(pos) > 0:
                    direction: Point3D = pos - sortation.position
                    brain_component.target_creature.valid = False
                    brain_component.target_position.setPosition(pos - Point3D(direction.x, direction.y, 0), PositionContext.SAFETY)
                else:
                    brain_component.target_creature.valid = False
                    brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 0), PositionContext.ROAM)
            else:
                brain_component.target_creature.valid = False
                brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 0), PositionContext.ROAM)
        elif brain_component.state == CreatureState.SLEEPING:
            if sleepy < 0.1:
                brain_component.state = CreatureState.AWAKE
