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
            'size': 1,
            'capacity': 100,
            'charge_loss': 1,
            'max_charge': 50,
            'max_discharge': 100,
            'cost' : 2000
        },
        'lead': {
            'size': 0.8,
            'capacity': 200,
            'charge_loss': 0.90,
            'max_charge': 25,
            'max_discharge': 50,
            'cost' : 1000
        },
        'palladium': {
            'size': 2,
            'capacity': 50,
            'charge_loss': 0.85,
            'max_charge': 100,
            'max_discharge': 100,
            'cost' : 1500
        }
    },
    'battery_types_used': ['lithium', 'lead', 'palladium'],
    'battery_counts': None,
    'warehouse_data': [
        {'area': 100, 'cost': 500},
        {'area': 100, 'cost': 10000},
        {'area': 100, 'cost': 20000},
        {'area': 100, 'cost': 50000},
        {'area': 100, 'cost': 100000}
    ],
    'warehouses_used': None
}

# Get warehouse and battery numbers
start_date = datetime.today() - timedelta(days=31)
date_range = get_preceding_30_days(start_date)

parameters['date_range'] = date_range

model, decision_var_dict, model_results, constraint_params = run(parameters)

# plot_result_time_series(model, decision_var_dict, model_results, constraint_params)

parameters['battery_counts'] = decision_var_dict['battery_counts']
parameters['warehouses_used'] = 'set'
parameters['date_range'] = [start_date.strftime("%Y%m%d")]

daily_profits = []
start_date = datetime.today() - timedelta(days=1)

for start_date in get_preceding_30_days(start_date):
    parameters['date_range'] = [start_date]

    [model, _, _, _] = run(parameters)

    daily_profits.append(model.objVal)

print(daily_profits)

time.sleep(5)

# Plot DVs
# plot_result_time_series(model, decision_var_dict, model_results, constraint_params)

# Plot waterfall profits
plot_waterfall_chart( parameters, daily_profits )