from ..ecs import ECSCoordinator
from .. import constants
from ..components.timer_component import TimerComponent

def timerUpdate(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.TIMER_COMPONENT):
        timer: TimerComponent = coordinator.getComponent(entity_id, constants.TIMER_COMPONENT)
        timer.current += 1
        if timer.current >= timer.time:
            for component_type, component_data in timer.add:
                coordinator.setComponent(entity_id, constants.componentPull(component_type), component_data if component_type != "timer" else TimerComponent(0, component_data.time, component_data.remove.copy(), component_data.add.copy()))
            coordinator.removeComponents(entity_id, set({constants.TIMER_COMPONENT}) | set(map(constants.componentPull, timer.remove)))