from ..ecs import ECSCoordinator
from .. import constants
from ..components.timer_component import TimerComponent

def timerUpdate(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.TIMER_COMPONENT):
        timer: TimerComponent = coordinator.getComponent(entity_id, constants.TIMER_COMPONENT)
        timer.current += 1
        if timer.current >= timer.time:
            for comp, dat in timer.add:
                coordinator.setComponent(entity_id, constants.componentPull(comp), dat if comp != "timer" else TimerComponent(0, dat.time, dat.remove.copy(), dat.add.copy()))
            coordinator.removeComponents(entity_id, set({constants.TIMER_COMPONENT}) | set(map(constants.componentPull, timer.remove)))