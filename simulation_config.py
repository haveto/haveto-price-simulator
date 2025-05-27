"""
Configuration data class for blockchain simulation parameters.
"""

from dataclasses import dataclass

@dataclass
class SimulationConfig:
    """
    Data class holding configuration parameters for the HaveTo blockchain simulation.
    Each attribute represents a tunable parameter that affects the behavior of the simulation.
    """
    block_time_seconds = 15
    simulation_years = 12
    yearly_inflation_rate = 0.10
    halving_interval_years = 4
    variable_adjustment_interval = 1000
    initial_nodes = 1
    initial_competition_cloud_host_cost_usd_per_month = 100
    initial_blockchain_miner_host_cost_usd_per_month = 80
    per_node_program_capacity_seconds = 3600
    single_program_size_seconds = 10
    gas_per_second = 10
    initial_gas_price_hvt = 0.0000001
    initial_hvt_price_usd = 8.0
    initial_reward = 11.29
    seconds_per_month = 30.5 * 24 * 3600
    active_program_exodus_rate = 0.05
    active_program_adding_rate = 0.9
    shard_base = 2
    debug_plot = ''
