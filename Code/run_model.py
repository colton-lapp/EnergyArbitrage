import os
import re
import time
import numpy as np
import pandas as pd
import gurobipy as gp
import sys
from gurobipy import GRB
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from web_scrape_price_data import extract_date, download_price_data, extract_time_series_prices
from make_plots import plot_price_time_series

# Set parameters for the model

# OPTIGUIDE DATA CODE GOES HERE

def create_model(parameters, batteries_counts=None, warehouses_used=None): # num_markets is going to be 1 for the time being
    name = parameters['name']
    generator_name = parameters['generator_name']
    date_range = parameters['date_range']
    num_periods = parameters['num_periods']
    num_markets = parameters['num_markets']
    # num_batteries = parameters['num_batteries']
    # battery_capacity = parameters['battery_capacity']
    # charge_loss = parameters['charge_loss']
    # max_charge = parameters['max_charge']
    # max_discharge = parameters['max_discharge']
    battery_types = parameters['battery_types']
    battery_types_used = parameters['battery_types_used']
    warehouse_data = parameters['warehouse_data']

    model = gp.Model(name)

    periods = range(num_periods)
    markets = range(num_markets)

    decision_var_dict = {}

    for battery_type in battery_types_used:
        for key in [f'{battery_type}-buy', f'{battery_type}-sell']:
            decision_var_dict[key] = model.addVars(num_periods, num_markets, vtype=GRB.CONTINUOUS, name=key, lb=0)

    # placeholder
    if date_range is None:
        start_date = datetime.today()
        start_date = start_date.strftime("%Y%m%d")
        date_range = [start_date]

    # Download data
    download_price_data(date_range, generator_name)

    # Plot prices time series
    # plot_price_time_series(date_range, generator_name)

    # Extract time series of prices in a list for Gurobi
    prices_dict = extract_time_series_prices(date_range, generator_name)
    price_times = prices_dict['times']
    prices = prices_dict['prices']

    objs = []
    total_area_needed = 0

    for battery_type in battery_types_used:
        battery = battery_types[battery_type]
        buy = decision_var_dict[f'{battery_type}-buy']
        sell = decision_var_dict[f'{battery_type}-sell']
        capacity = battery['capacity']
        charge_loss = battery['charge_loss']
        max_charge = battery['max_charge']
        max_discharge = battery['max_discharge']
        size = battery['size']

        if batteries_counts is None:
            num_batteries = model.addVar(vtype=GRB.INTEGER, name=f'Number of {battery_type} batteries', lb=0)
            decision_var_dict[f'{battery_type}_num'] = num_batteries
        else:
            num_batteries = batteries_counts[battery_type]

        total_area_needed += num_batteries * size

        objs = objs + [prices[p] * sell[p, i] - prices[p] * buy[p, i] for p in periods for i in markets]

        for p in range(num_periods):
            current_level = np.sum(charge_loss * buy[p_, i] - sell[p_, i] for p_ in range(p) for i in markets)

            for i in markets:
                model.addConstr(current_level <= capacity * num_batteries, f'CapacityConstraint_period_{p+1}')
                model.addConstr(sell[p, i] <= current_level, f'SupplyConstraint_period_{p+1}')
                model.addConstr(buy[p, i] * charge_loss <= max_charge, f'ChargeConstraint_period_{p+1}')
                model.addConstr(sell[p, i] <= max_discharge, f'DischargeConstraint_period_{p+1}')

    if warehouses_used is None:
        warehouses_used = model.addVars(len(warehouse_data), vtype=GRB.BINARY, name=f'Number of warehouses')
        decision_var_dict['warehouses_used'] = warehouses_used

    model.update()

    model.addConstr(
        gp.quicksum(warehouse_data[i]['area'] * warehouses_used[i] for i, warehouse in enumerate(warehouse_data)) >= total_area_needed,
        name="Area_constraint"
    )

    objs = objs + [warehouse_data[i]['cost'] * warehouses_used[i] * -1 for i, warehouse in enumerate(warehouse_data)]

    model.update()

    model.setObjective(
        gp.quicksum(objs),
        GRB.MAXIMIZE
    )
    # OPTIGUIDE CONSTRAINT CODE GOES HERE

    return [model, decision_var_dict]


# Run the model
def run(parameters, print_results=False):
    battery_types_used = parameters['battery_types_used']

    # Create model
    [model, decision_var_dict] = create_model(parameters)

    # Run model
    model.optimize()

    if print_results:
        num_periods = parameters['num_periods']
        num_markets = parameters['num_markets']

        if model.status == GRB.OPTIMAL:
            print("\nOptimal Solution:")

            for p in range(num_periods):
                print(f"\nPeriod {p + 1}:")

                for battery_type in battery_types_used:
                    buy = decision_var_dict[f'{battery_type}-buy']
                    sell = decision_var_dict[f'{battery_type}-sell']

                    print(f"\nFor Battery Type: {battery_type}:")
                    for i in range(num_markets):
                        print(f"Buy from Market {i + 1}: {buy[p, i].x}")
                        print(f"Sell to Market {i + 1}: {sell[p, i].x}")

            print(f"\nTotal Profit: {model.objVal}")
        else:
            print("No solution found")

    return [model, decision_var_dict]