from src.simulation import Simulation

def debugStart(simulation: Simulation) -> None:
    ...

def debugUpdate(simulation: Simulation) -> None:
    ...

def debugDisplay(simulation: Simulation) -> None:
    ...

def debugInput(simulation: Simulation, input: str) -> None:
    match input:
        case "quit":
            simulation["running"] = False

def main():
    debugSimulation: Simulation = Simulation(debugStart, debugUpdate, debugDisplay, debugInput, {
        "running": True
    })
    debugSimulation.start(debugSimulation)
    while debugSimulation["running"]:
        debugSimulation.update(debugSimulation)
        debugSimulation.display(debugSimulation)
        debugSimulation.input(debugSimulation, input())
        

if __name__ == "__main__":
    main()