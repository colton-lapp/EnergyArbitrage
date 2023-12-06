from run_model import run
from make_plots import plot_result_time_series, plot_waterfall_chart
from web_scrape_price_data import get_preceding_30_days
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go


parameters = {
    'name': 'ElectricityArbitrage',
    'generator_name': 'ADK HUDSON___FALLS',
    'date_range': None,
    'num_markets': 1,
    'battery_types': {
        'lithium': {
            'size': 18,
            'capacity': 150,
            'charge_loss': 0.96,
            'max_charge': 120,
            'max_discharge': 20,
            'cost': 2500
        },
        'lead': {
            'size': 14,
            'capacity': 350,
            'charge_loss': 0.88,
            'max_charge': 5,
            'max_discharge': 50,
            'cost': 500
        },
        'palladium': {
            'size': 8,
            'capacity': 100,
            'charge_loss': 0.5,
            'max_charge': 100,
            'max_discharge': 100,
            'cost': 4500
        }
    },
    'battery_types_used': ['lithium', 'lead', 'palladium'],
    'battery_counts': None,
    'warehouse_data': [
        {'area': 100, 'cost': 50000},
        {'area': 100, 'cost': 100000},
        {'area': 100, 'cost': 200000},
        {'area': 100, 'cost': 500000},
        {'area': 100, 'cost': 1000000}
    ],
    'warehouses_used': None,
    'carry_over': False
}

# Battery numbers
def stage_one(start_date, parameters):
    date_range = get_preceding_30_days(start_date)
    parameters['date_range'] = date_range

    return run(parameters)

def stage_two(start_date, parameters, decision_var_dict):
    parameters['battery_counts'] = decision_var_dict['battery_counts']
    parameters['warehouses_used'] = 'set'
    parameters['date_range'] = [start_date.strftime("%Y%m%d")]

    daily_profits = []
    start_date = datetime.today() - timedelta(days=1)

    for start_date in get_preceding_30_days(start_date):
        parameters['date_range'] = [start_date]

        [model, _, _, _] = run(parameters)

        daily_profits.append(model.objVal)

    return daily_profits

start_date = datetime.today() - timedelta(days=31)

model, decision_var_dict, model_results, constraint_params = stage_one(start_date, parameters)

daily_profits = stage_two(start_date, parameters, decision_var_dict)

print(daily_profits)
print(decision_var_dict['battery_counts'])

time.sleep(5)

# Plot DVs
# plot_result_time_series(model, decision_var_dict, model_results, constraint_params)

# # Plot waterfall profits
# plot_waterfall_chart(parameters, daily_profits)