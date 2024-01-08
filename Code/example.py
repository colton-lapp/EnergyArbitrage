import time
from datetime import datetime, timedelta

from make_plots import plot_result_time_series, plot_waterfall_chart
from two_stage import stage_one, stage_two

import plotly.graph_objects as go

# Set parameters for the model

parameters = {
    'name': 'ElectricityArbitrage',
    'generator_name': 'ADK HUDSON___FALLS',
    'date_range': None,
    'num_markets': 1,
    'battery_types': {
        'lithium': {
            'size': 22.1,
            'capacity': 100,
            'charge_loss': 0.75,
            'max_charge': 40,
            'max_discharge': 15,
            'cost': 12500
        },
        'lead': {
            'size': 20.3,
            'capacity': 350,
            'charge_loss': 0.68,
            'max_charge': 10,
            'max_discharge': 40,
            'cost': 11000
        },
        'palladium': {
            'size': .1,
            'capacity': 5,
            'charge_loss': 0.33,
            'max_charge': 5,
            'max_discharge': 5,
            'cost': 50
        }
    },
    'battery_types_used': ['lithium', 'lead', 'palladium'],
    'battery_counts': None,
    'warehouse_data': [
        {'area': 100, 'cost': 30000},
        {'area': 100, 'cost': 50000},
        {'area': 100, 'cost': 100000},
        {'area': 100, 'cost': 300000},
        {'area': 100, 'cost': 8000000}
    ],
    'warehouses_used': None,
    'carry_over': False
}

start_date = datetime.today() - timedelta(days=31)

model, decision_var_dict, model_results, constraint_params = stage_one(start_date, parameters)

daily_profits = stage_two(start_date, parameters, decision_var_dict)

print(daily_profits)
print(decision_var_dict['battery_counts'])

time.sleep(1)

# Plot DVs
plot_result_time_series(model, decision_var_dict, model_results, constraint_params)

time.sleep(1)

# # Plot waterfall profits
plot_waterfall_chart(parameters, decision_var_dict, daily_profits)