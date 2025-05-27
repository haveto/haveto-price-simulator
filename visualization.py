"""
Contains functions to visualize blockchain simulation results.

The main function, `plot_simulation`, takes a simulation log (list of dictionaries),
converts it into a pandas DataFrame, and produces an interactive multi-line chart
using Plotly to display various numeric metrics over block height.

This visualization aids in analyzing the progression and trends of blockchain simulation metrics.
"""
import pandas as pd
import plotly.express as px

def plot_simulation(log):
    """
    Visualizes the blockchain simulation log using Plotly.

    Converts the simulation log (a list of dictionaries) into a DataFrame
    and generates a multi-line chart showing the change in various numeric 
    metrics over block height.

    Parameters:
    ----------
    log : list of dict
        The simulation output log containing metrics for each block. 
        Each dictionary should represent a block with key-value pairs 
        of metric names and values (including a 'height' key).

    Returns:
    -------
    None
        Displays an interactive Plotly line chart in the browser.
    """
    df = pd.DataFrame(log)

    # Plot only numeric columns—avoid mixed dtypes
    numeric_cols = df.select_dtypes(include=["number"]).columns
    y_cols = [col for col in numeric_cols if col != "block"]

    fig = px.line(
        df,
        x="height",
        y=y_cols,
        title="HaveTo Simulation – All Metrics Over height",
        labels={"value": "Value", "variable": "Metric"},
    )

    fig.update_layout(legend_title_text="Metrics", hovermode="x unified")
    fig.show()
