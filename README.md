# haveto.com Simulation

To model the tokenomics of haveto.com with realistic economic behavior, we developed a **12 years** Python-based simulation. This simulation incorporates dynamic variables such as block rewards, network congestion, developer adoption, sharding mechanics, gas fee adjustments,
miner profitability, and inflationary hosting costs.

Key features of the simulation:
- **Block Time**: 15 seconds
- **Total Duration**: 12 years
- **Initial Gas Price**: 0.0000001 HVT
- **Initial Coin Price**: 8 USD
- **Initial Block Reward**: 11.29 HVT
- **Sharding**: Auto-scaling sharding based on network congestion.
- **Cloud Hosting Costs**: Both blockchain miner costs and competition cloud hosting costs increase over time with an annual inflation rate of 10%.

## Visualization

The simulation includes a dynamic visualization using Plotly that charts the following metrics over time:
- Current Nodes
- Active Programs
- Gas Price In USD & haveto.com
- haveto.com Price
- Sharding Degree
- Current Reward
- Cost Per Program On Chain
- Cost Per Program On Cloud

## Usage

To run the simulation, ensure that you have Python 3.x installed, along with the following dependencies:

```bash
pip install -r requirements.txt
```

Run the script:

```bash
python manual.py
```
This will execute the simulation, logging data and visualizing the results in a Plotly chart.
