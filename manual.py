import random
import pandas as pd
from tqdm import tqdm

def total_blocks(years: int, block_time: int) -> int:
    return int(years * 365.25 * 24 * 3600 // block_time)

def montly_blocks(months: int, block_time: int) -> int:
    return int(months * 30.5 * 24 * 3600 // block_time)

DEBUG_PLOT=0

yearly_inflation_rate=0.10
halving_interval_year=4
simulation_years=12
block_time_seconds=15
variable_adjustment_internval=1000
initial_competition_cloud_host_cost_usd_per_month = 100
initial_blockchain_miner_host_cost_usd_per_month = 80
initial_nodes=1
per_node_program_capacity_seconds=3600
single_program_size_seconds=10
gas_per_second=10
initial_gas_price_hvt=0.0000001
initial_hvt_price_usd=8.0
initial_gas_price_usd=initial_gas_price_hvt*initial_hvt_price_usd
blocks_tobe_mined=total_blocks(years=simulation_years,block_time=block_time_seconds)
initial_reward=11.29
seconds_per_month = 30.5 * 24 * 3600
gas_per_program = gas_per_second * single_program_size_seconds
active_program_max_pricing_usd = []
active_program_exodus_rate=0.05
active_program_adding_rate=0.9

# updating vars
competition_cloud_host_cost_usd_per_month=initial_competition_cloud_host_cost_usd_per_month # done
blockchain_miner_host_cost_usd_per_month=initial_blockchain_miner_host_cost_usd_per_month # done
current_nodes=initial_nodes
current_gas_price_hvt=initial_gas_price_hvt
current_hvt_price_usd=initial_hvt_price_usd # done but sharding pending
current_gas_price_usd=current_gas_price_hvt*current_hvt_price_usd
congestion=0
active_program=0
current_reward=initial_reward # done
total_network_cost_month=current_nodes*blockchain_miner_host_cost_usd_per_month # done
cost_per_program_on_chain_usd=0 # done
cost_per_program_on_competition_usd=0 # done
cumu_total_network_cost_month=0
shard_degree=0
shard_base=2
shard_count=shard_base**shard_degree
miner_cost_hvt=0

total_hvt_supply = 0
miner_saving_hvt = 100
miner_revenue_hvt = 0
miner_revenue_usd = 0
miner_revenue_reward_hvt = 0
miner_revenue_gas_hvt = 0

def height_to_year(height):
    return height//total_blocks(1, block_time=block_time_seconds)

def simulate_cloud_pricing(year):
    global competition_cloud_host_cost_usd_per_month, blockchain_miner_host_cost_usd_per_month, total_network_cost_month, cumu_total_network_cost_month
    competition_cloud_host_cost_usd_per_month = initial_competition_cloud_host_cost_usd_per_month * ((1 + yearly_inflation_rate)**year)
    blockchain_miner_host_cost_usd_per_month = initial_blockchain_miner_host_cost_usd_per_month * ((1 + yearly_inflation_rate)**year)
    total_network_cost_month=current_nodes * blockchain_miner_host_cost_usd_per_month
    cumu_total_network_cost_month += total_network_cost_month



def simulate_program_runner(year):
    global current_gas_price_usd, active_program, current_gas_price_hvt, congestion, DEBUG_PLOT
    congestion = calculate_congesion(active_program)
    if congestion > 0.5:
        current_gas_price_hvt *= 1.012
    else:
        current_gas_price_hvt *= 0.98
    if current_gas_price_hvt < 1e-18:
        current_gas_price_hvt = 1e-18
    current_gas_price_usd = current_gas_price_hvt * current_hvt_price_usd / shard_count
    

    

def run_investor(year):
    global miner_revenue_hvt, miner_revenue_usd, miner_cost_hvt, current_nodes, miner_revenue_reward_hvt, miner_revenue_gas_hvt, miner_saving_hvt, DEBUG_PLOT
    

    miner_revenue_reward_hvt = (current_reward * montly_blocks( months=1, block_time=block_time_seconds))
    miner_revenue_gas_hvt = (current_gas_price_hvt * active_program * gas_per_program)

    miner_revenue_hvt = miner_revenue_reward_hvt + miner_revenue_gas_hvt
    miner_revenue_usd = miner_revenue_hvt * current_hvt_price_usd
    

    div = max(current_hvt_price_usd, 1)
    miner_cost_hvt = (current_nodes * blockchain_miner_host_cost_usd_per_month) / div

    miner_saving_hvt += (miner_revenue_hvt - miner_cost_hvt)
    # print(miner_saving_hvt)
    # if miner_saving_hvt < 0:
    #     import sys
    #     sys.exit()


    if miner_saving_hvt >= (blockchain_miner_host_cost_usd_per_month/div) * 1.2:
        current_nodes += 1
        miner_saving_hvt -= (blockchain_miner_host_cost_usd_per_month / div)

    if miner_saving_hvt <= 0:
        if current_nodes > 1:
            current_nodes -= 1
            miner_saving_hvt += (blockchain_miner_host_cost_usd_per_month / div)
    


def run_shard_manager(year):
    global shard_degree, shard_count, shard_base, congestion
    if congestion < 0.05:
        if shard_degree > 0:
            shard_degree -= 1
            shard_count = shard_base**shard_degree
    if congestion > 0.30:
        if current_nodes > (shard_base**(shard_degree+1)):
            shard_degree += 1
            shard_count = shard_base**shard_degree
    congestion = calculate_congesion(active_program)

def simulate_miner(year):
    global current_reward, miner_revenue_hvt, total_hvt_supply
    four_year_interval = (year+1) // 4
    
    current_reward=initial_reward/(2 ** four_year_interval)
    total_hvt_supply +=  current_reward
    simulate_program_runner(year)
    run_investor(year)
    run_shard_manager(year)

    
    

def simulate_market(year):
    global current_hvt_price_usd
    blocks_a_month = montly_blocks(months=1, block_time=block_time_seconds)
    
    # current_hvt_price_usd = total_network_cost_month / (current_gas_price_hvt + (current_reward * montly_blocks(months=1, block_time=block_time_seconds))) # sharding pending
    
    current_hvt_price_usd = (cumu_total_network_cost_month) / total_hvt_supply


def calculate_congesion(active_program):
    # count = variable_adjustment_internval * per_node_program_capacity_seconds / single_program_size_seconds
    count = variable_adjustment_internval * shard_count * per_node_program_capacity_seconds / single_program_size_seconds
    return min(active_program / count, 1.0)
    
def simulate_developers(year):
    global active_program, cost_per_program_on_chain_usd, cost_per_program_on_competition_usd, congestion, active_program_max_pricing_usd, DEBUG_PLOT
    
    cost_per_program_on_chain_usd = (current_gas_price_usd) * gas_per_program 
    cost_per_program_on_competition_usd = competition_cloud_host_cost_usd_per_month * single_program_size_seconds / seconds_per_month

    # print(year, "=="*10)
    

    # print(current_hvt_price_usd)
    # print(current_gas_price_usd)
    # print(shard_degree)
    # print(active_program)
    
    new_active_program = int(variable_adjustment_internval*shard_count*active_program_adding_rate)

    if calculate_congesion(active_program+new_active_program) <= 1.0 and cost_per_program_on_competition_usd >= cost_per_program_on_chain_usd:
        # active_program_max_pricing_usd += [(cost_per_program_on_chain_usd+(random.random()*cost_per_program_on_chain_usd) )for i in range(new_active_program)]
        active_program += new_active_program
        # print("asdasd",min(active_program_max_pricing_usd),  max(active_program_max_pricing_usd))
        # print(cost_per_program_on_chain_usd, cost_per_program_on_competition_usd)
    
    if cost_per_program_on_competition_usd < cost_per_program_on_chain_usd:
        # print(active_program_max_pricing_usd)
        # print("asdasd",min(active_program_max_pricing_usd),  max(active_program_max_pricing_usd))
        
        # print(cost_per_program_on_chain_usd, cost_per_program_on_competition_usd)
        # old_active_program_max_pricing_usd = sorted(active_program_max_pricing_usd)
        
        # remain_ratio = 1.0 - active_program_exodus_rate

        # active_program_max_pricing_usd = active_program_max_pricing_usd[int(-1*remain_ratio*len(active_program_max_pricing_usd)):]
        # active_program = len(active_program_max_pricing_usd)
        active_program = int(active_program*(1-active_program_exodus_rate))
        
        # if active_program == 0:
        #     print("active_program")
        #     import sys
        #     sys.exit()
        
    DEBUG_PLOT = active_program
    congestion = calculate_congesion(active_program)
    

log = []

for height in tqdm(range(0, blocks_tobe_mined, variable_adjustment_internval)):
    year = height_to_year(height)
    simulate_cloud_pricing(year)
    simulate_developers(year)
    simulate_miner(year)
    simulate_market(year)
    


    log.append({
        'height':height,
        'competition_cloud_host_cost_usd_per_month': competition_cloud_host_cost_usd_per_month,
        'blockchain_miner_host_cost_usd_per_month': blockchain_miner_host_cost_usd_per_month,
        'current_nodes':current_nodes,
        'current_gas_price_hvt':current_gas_price_hvt,
        'current_hvt_price_usd':current_hvt_price_usd,
        'current_gas_price_usd':current_gas_price_usd,
        'congestion':congestion,
        'active_program':active_program,
        'current_reward':current_reward,
        "total_network_cost_month":total_network_cost_month,
        "cost_per_program_on_chain_usd":cost_per_program_on_chain_usd, 
        "cost_per_program_on_competition_usd":cost_per_program_on_competition_usd,
        "miner_revenue_hvt": miner_revenue_hvt,
        "miner_revenue_reward_hvt":miner_revenue_reward_hvt,
        "miner_revenue_gas_hvt":miner_revenue_gas_hvt,
        "cumu_total_network_cost_month":cumu_total_network_cost_month,
        "total_hvt_supply":total_hvt_supply,
        "miner_saving_hvt": miner_saving_hvt,
        "shard_count": shard_count,
        "shard_degree": shard_degree,
        "miner_cost_hvt":miner_cost_hvt,
        "miner_revenue_usd": miner_revenue_usd,
        # "DEBUG_PLOT": DEBUG_PLOT
    })

import plotly.express as px

df = pd.DataFrame(log)



# Plot only numeric columns—avoid mixed dtypes
numeric_cols = df.select_dtypes(include=["number"]).columns
y_cols = [col for col in numeric_cols if col != "block"]
# y_cols = [col for col in numeric_cols if col in [
#     "block", 
#     # "miner_revenue_gas_hvt", 
#     "DEBUG_PLOT"
# ]]

fig = px.line(
    df,
    x="height",
    y=y_cols,
    title="HaveTo Simulation – All Metrics Over height",
    labels={"value": "Value", "variable": "Metric"},
)
fig.update_layout(legend_title_text="Metrics", hovermode="x unified")
fig.show()



    

