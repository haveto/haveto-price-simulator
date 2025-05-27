"""
This script initializes and runs a blockchain simulation and then visualizes the results.
It uses the `BlockchainSimulation` class to simulate the behavior of a blockchain over time,
and the `plot_simulation` function to generate a visual representation of the simulation log.

Modules:
    - simulation: Contains the BlockchainSimulation class 
        for modeling tokenomics, sharding, and network parameters.
    - visualization: Contains the plot_simulation function for rendering simulation output.
"""
from simulation import BlockchainSimulation
from visualization import plot_simulation

def main():
    """
    Create an instance of the BlockchainSimulation, execute the simulation, 
    and visualize the logged results using a plotting utility.
    """
    sim = BlockchainSimulation()
    sim.run_simulation()
    plot_simulation(sim.log)

if __name__ == "__main__":
    main()
