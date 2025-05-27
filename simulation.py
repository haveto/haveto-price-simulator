"""
This module contains the `BlockchainSimulation` class, which simulates the economic and behavioral
dynamics of a decentralized blockchain over a multi-year period.

The simulation models:
- Miner economics (costs, rewards, and adaptive behavior)
- Developer decision-making (blockchain vs. traditional cloud hosting)
- Network congestion and adaptive sharding
- Token supply, gas pricing, and market dynamics

The core functionality involves running a full simulation over a configurable number of years,
logging all economic variables and system metrics at regular intervals to understand how 
the blockchain behaves under varying economic conditions.

Dependencies:
- tqdm: For progress display
- utils: Contains helper functions like `total_blocks`, `monthly_blocks`, and `height_to_year`
"""
from tqdm import tqdm
from utils import total_blocks, montly_blocks, height_to_year
from simulation_config import SimulationConfig

class BlockchainSimulation:
    """
    A simulation class for modeling a blockchain-based computation network.
    It models token economics, miner and developer behavior, sharding, and market dynamics.

    Key components:
        - Miners earn tokens through rewards and gas fees.
        - Developers choose between blockchain and competition based on cost.
        - Network adjusts sharding based on congestion.
        - Gas price and token price evolve over time.
    """
    def __init__(self):
        """
        Initializes 
            - constants
            - simulation parameters
            - system state 
        """
        # State
        self.config = SimulationConfig()

        self.initial_gas_price_usd = \
            self.config.initial_gas_price_hvt * self.config.initial_hvt_price_usd
        self.blocks_tobe_mined = total_blocks(
            years=self.config.simulation_years,
            block_time = self.config.block_time_seconds
        )
        self.gas_per_program = self.config.gas_per_second * self.config.single_program_size_seconds
        self.active_program_max_pricing_usd = []

        self.competition_cloud_host_cost_usd_per_month = \
            self.config.initial_competition_cloud_host_cost_usd_per_month
        self.blockchain_miner_host_cost_usd_per_month = \
            self.config.initial_blockchain_miner_host_cost_usd_per_month
        self.current_nodes = self.config.initial_nodes

        self.current_gas_price_hvt = self.config.initial_gas_price_hvt
        self.current_hvt_price_usd = self.config.initial_hvt_price_usd
        self.current_gas_price_usd = \
            self.current_gas_price_hvt * self.current_hvt_price_usd

        self.congestion = 0
        self.active_program = 0
        self.current_reward = self.config.initial_reward

        self.total_network_cost_month = \
            self.current_nodes * self.blockchain_miner_host_cost_usd_per_month
        self.cost_per_program_on_chain_usd = 0
        self.cost_per_program_on_competition_usd = 0
        self.cumu_total_network_cost_month = 0
        self.shard_degree = 0
        self.shard_count = self.config.shard_base ** self.shard_degree
        self.miner_cost_hvt=0

        self.total_hvt_supply = 0
        self.miner_saving_hvt = 100
        self.miner_revenue_hvt = 0
        self.miner_revenue_usd = 0
        self.miner_revenue_reward_hvt = 0
        self.miner_revenue_gas_hvt = 0
        self.log = []

    def simulate_cloud_pricing(self, year):
        """
        Adjusts hosting costs based on yearly inflation.
        """
        self.competition_cloud_host_cost_usd_per_month = \
            self.config.initial_competition_cloud_host_cost_usd_per_month * \
                ((1 + self.config.yearly_inflation_rate)**year)
        self.blockchain_miner_host_cost_usd_per_month = \
            self.config.initial_blockchain_miner_host_cost_usd_per_month * \
                ((1 + self.config.yearly_inflation_rate)**year)
        self.total_network_cost_month = \
            self.current_nodes * self.blockchain_miner_host_cost_usd_per_month
        self.cumu_total_network_cost_month += self.total_network_cost_month

    def calculate_congesion(self, active_program):
        """
        Calculate the network congestion ratio based on the number of active programs.

        Args:
            active_program (int or float): 
                The current number of active programs running on the network.

        Returns:
            float: Congestion ratio, ranging from 0.0 to 1.0.
                - 0.0 means no congestion.
                - 1.0 means full congestion or overutilization.
        """
        count = self.config.variable_adjustment_interval * self.shard_count * \
            self.config.per_node_program_capacity_seconds / self.config.single_program_size_seconds
        return min(active_program / count, 1.0)

    def simulate_program_runner(self):
        """
        Adjusts gas price based on network congestion.
        """
        self.congestion = self.calculate_congesion(self.active_program)
        if self.congestion > 0.5:
            self.current_gas_price_hvt *= 1.012
        else:
            self.current_gas_price_hvt *= 0.98

        self.current_gas_price_hvt = max(self.current_gas_price_hvt, 1e-18)

        self.current_gas_price_usd = \
            self.current_gas_price_hvt * self.current_hvt_price_usd / self.shard_count

    def run_investor(self):
        """
        Simulates miner profit, adjusts nodes based on profitability.
        """
        self.miner_revenue_reward_hvt = (
            self.current_reward * montly_blocks(
                months=1,
                block_time = self.config.block_time_seconds
            )
        )
        self.miner_revenue_gas_hvt = (
            self.current_gas_price_hvt * self.active_program * self.gas_per_program
        )

        self.miner_revenue_hvt = self.miner_revenue_reward_hvt + self.miner_revenue_gas_hvt
        self.miner_revenue_usd = self.miner_revenue_hvt * self.current_hvt_price_usd

        div = max(self.current_hvt_price_usd, 1)
        self.miner_cost_hvt = \
            (self.current_nodes * self.blockchain_miner_host_cost_usd_per_month) / div

        self.miner_saving_hvt += (self.miner_revenue_hvt - self.miner_cost_hvt)

        if self.miner_saving_hvt >= (self.blockchain_miner_host_cost_usd_per_month/div) * 1.2:
            self.current_nodes += 1
            self.miner_saving_hvt -= (self.blockchain_miner_host_cost_usd_per_month / div)

        if self.miner_saving_hvt <= 0:
            if self.current_nodes > 1:
                self.current_nodes -= 1
                self.miner_saving_hvt += (self.blockchain_miner_host_cost_usd_per_month / div)

    def run_shard_manager(self):
        """
        Dynamically increases or decreases the shard count based on congestion level.
        """
        if self.congestion < 0.05:
            if self.shard_degree > 0:
                self.shard_degree -= 1
                self.shard_count = self.config.shard_base**self.shard_degree
        if self.congestion > 0.30:
            if self.current_nodes > (self.config.shard_base**(self.shard_degree+1)):
                self.shard_degree += 1
                self.shard_count = self.config.shard_base**self.shard_degree
        self.congestion = self.calculate_congesion(self.active_program)

    def simulate_miner(self, year):
        """
        Simulates miner economics including halving reward, gas income, and shard adjustment.

        Args:
            year (int): Current simulation year.
        """
        four_year_interval = (year+1) // 4

        self.current_reward = self.config.initial_reward/(2 ** four_year_interval)
        self.total_hvt_supply +=  self.current_reward
        self.simulate_program_runner()
        self.run_investor()
        self.run_shard_manager()

    def simulate_market(self):
        """
        Simulate the current market price of the HVT token based on network costs and supply.
        This function calculates the HVT token price in USD by dividing the cumulative monthly
        network cost by the total supply of HVT tokens.

        Returns:
            float: The updated HVT token price (`current_hvt_price_usd`).

        Notes:
            - `cumu_total_network_cost_month` represents the total network cost for the month.
            - `total_hvt_supply` is the total circulating supply of HVT tokens.
        """
        return (self.cumu_total_network_cost_month) / self.total_hvt_supply

    def simulate_developers(self):
        """
        Simulates developer behavior in response to relative 
        costs of using blockchain vs competitors.
        """
        self.cost_per_program_on_chain_usd = (self.current_gas_price_usd) * self.gas_per_program
        self.cost_per_program_on_competition_usd = \
            self.competition_cloud_host_cost_usd_per_month * \
                self.config.single_program_size_seconds / self.config.seconds_per_month

        new_active_program = int(
            self.config.variable_adjustment_interval * \
                self.shard_count * self.config.active_program_adding_rate
        )

        if (
            self.calculate_congesion(self.active_program + new_active_program) <= 1.0 \
                and self.cost_per_program_on_competition_usd >= self.cost_per_program_on_chain_usd
        ):
            self.active_program += new_active_program

        if self.cost_per_program_on_competition_usd < self.cost_per_program_on_chain_usd:
            self.active_program = int(
                self.active_program * (1 - self.config.active_program_exodus_rate)
            )

        self.config.debug_plot = self.active_program
        self.congestion = self.calculate_congesion(self.active_program)

    def run_simulation(self):
        """
        Runs the full simulation loop across all blocks and logs the results.
        """
        for height in tqdm(
            range(0, self.blocks_tobe_mined, self.config.variable_adjustment_interval)
        ):
            year = height_to_year(height, self.config.block_time_seconds)

            self.simulate_cloud_pricing(year)
            self.simulate_developers()
            self.simulate_miner(year)
            self.current_hvt_price_usd = self.simulate_market()

            self.log.append({
                'height':height,
                'competition_cloud_host_cost_usd_per_month' : \
                    self.competition_cloud_host_cost_usd_per_month,
                'blockchain_miner_host_cost_usd_per_month' : \
                    self.blockchain_miner_host_cost_usd_per_month,
                'current_nodes' : self.current_nodes,
                'current_gas_price_hvt' : self.current_gas_price_hvt,
                'current_hvt_price_usd' : self.current_hvt_price_usd,
                'current_gas_price_usd' : self.current_gas_price_usd,
                'congestion' : self.congestion,
                'active_program' : self.active_program,
                'current_reward' : self.current_reward,
                "total_network_cost_month" : self.total_network_cost_month,
                "cost_per_program_on_chain_usd" : self.cost_per_program_on_chain_usd, 
                "cost_per_program_on_competition_usd" : self.cost_per_program_on_competition_usd,
                "miner_revenue_hvt" : self.miner_revenue_hvt,
                "miner_revenue_reward_hvt" : self.miner_revenue_reward_hvt,
                "miner_revenue_gas_hvt" : self.miner_revenue_gas_hvt,
                "cumu_total_network_cost_month" : self.cumu_total_network_cost_month,
                "total_hvt_supply" : self.total_hvt_supply,
                "miner_saving_hvt" : self.miner_saving_hvt,
                "shard_count" : self.shard_count,
                "shard_degree" : self.shard_degree,
                "miner_cost_hvt" : self.miner_cost_hvt,
                "miner_revenue_usd" : self.miner_revenue_usd,
                # "debug_plot": debug_plot
            })
