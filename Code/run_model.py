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

parameters = {
    'name': 'ElectricityArbitrage',
    'generator_name': 'ADK HUDSON___FALLS',
    'start_date': None,
    'num_periods': 24,
    'num_markets': 1,
    'num_batteries': 8,
    'battery_capacity': 100,
    'charge_loss': 0.95,
    'max_charge': 50,
    'max_discharge': 100
}

# OPTIGUIDE DATA CODE GOES HERE


def create_model(parameters): # num_markets is going to be 1 for the time being
    name = parameters['name']
    generator_name = parameters['generator_name']
    start_date = parameters['start_date']
    num_periods = parameters['num_periods']
    num_markets = parameters['num_markets']
    num_batteries = parameters['num_batteries']
    battery_capacity = parameters['battery_capacity']
    charge_loss = parameters['charge_loss']
    max_charge = parameters['max_charge']
    max_discharge = parameters['max_discharge']

    model = gp.Model(name)

    periods = range(num_periods)
    markets = range(num_markets)

    buy = model.addVars(num_periods, num_markets, vtype=GRB.CONTINUOUS, name='Buy')
    sell = model.addVars(num_periods, num_markets, vtype=GRB.CONTINUOUS, name='Sell')


    # placeholder
    if start_date is None:
        start_date = datetime.today()
        start_date = start_date.strftime("%Y%m%d")

    # Download data
    download_price_data(start_date, generator_name)

    # Plot prices time series
    plot_price_time_series( start_date, generator_name)

    # Extract time series of prices in a list for Gurobi
    prices_dict = extract_time_series_prices( start_date, generator_name)
    price_times = prices_dict['times']
    prices = prices_dict['prices']





    #model.setObjective(
    #    gp.quicksum(prices[p][i] * sell[p, i] - prices[p][i] * buy[p, i] for p in periods for i in markets),
    #    GRB.MAXIMIZE
    #)

    model.setObjective(
        gp.quicksum(prices[p] * sell[p, i] - prices[p] * buy[p, i] for p in periods for i in markets),
        GRB.MAXIMIZE
    )

    for p in range(num_periods):
        current_level = np.sum(charge_loss * buy[p_, i] - sell[p_, i] for p_ in range(p) for i in markets)

        # model.addConstr(current_level <= 0, f'EnoughToSellConstraint_period_{p+1}')

        for i in markets:
            model.addConstr(current_level <= battery_capacity * num_batteries, f'CapacityConstraint_period_{p+1}')
            model.addConstr(sell[p, i] <= current_level, f'SupplyConstraint_period_{p+1}')
            model.addConstr(buy[p, i] * charge_loss <= max_charge, f'ChargeConstraint_period_{p+1}')
            model.addConstr(sell[p, i] <= max_discharge, f'DischargeConstraint_period_{p+1}')

    # OPTIGUIDE CONSTRAINT CODE GOES HERE

    return [model, buy, sell]


# Run the model 
def run(parameters, print_results = False ):

    # Create model
    [model, buy, sell] = create_model(parameters)

    # Run model
    model.optimize()

    if print_results:
        num_periods = parameters['num_periods']
        num_markets = parameters['num_markets']

        if model.status == GRB.OPTIMAL:
            print("\nOptimal Solution:")

            for p in range(num_periods):
                print(f"\nPeriod {p + 1}:")

                for i in range(num_markets):
                    print(f"Buy from Market {i + 1}: {buy[p, i].x}")
                    print(f"Sell to Market {i + 1}: {sell[p, i].x}")

            print(f"\nTotal Profit: {model.objVal}")
        else:
            print("No solution found")

    return [model, buy, sell]


run(parameters, print_results = True )