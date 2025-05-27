"""
This module provides utility functions for calculating blockchain block production metrics
based on time intervals and block mining duration.

Functions:
- total_blocks(years: int, block_time: int) -> int
    Calculates the total number of blocks mined over a specified number of years.

- montly_blocks(months: int, block_time: int) -> int
    Calculates the total number of blocks mined over a specified number of months.

- height_to_year(height: int, block_time_seconds: int) -> int
    Converts a block height into the number of years since the genesis block, given the block time.

These functions are useful for blockchain simulations 
and analytics where understanding block production over time is essential.
"""

def total_blocks(years: int, block_time: int) -> int:
    """
    Calculate the total number of blocks produced over a given number of years.

    Args:
        years (int): The number of years to calculate blocks for.
        block_time (int): Time to mine a block (in seconds).

    Returns:
        int: Total number of blocks produced in the given years.
    """
    return int(years * 365.25 * 24 * 3600 // block_time)

def montly_blocks(months: int, block_time: int) -> int:
    """
    Calculate the total number of blocks produced over a given number of months.

    Args:
        months (int): The number of months to calculate blocks for.
        block_time (int): Time to mine a block (in seconds).

    Returns:
        int: Total number of blocks produced in the given months.
    """
    return int(months * 30.5 * 24 * 3600 // block_time)

def height_to_year(height, block_time_seconds):
    """
    Convert a given block height to the number of years since the genesis block.

    Args:
        height (int): The block height to convert.
        block_time_seconds (int): Time to mine each block in seconds.

    Returns:
        int: The number of whole years that have passed based on the block height.
    """
    return height//total_blocks(1, block_time=block_time_seconds)
