from run_model import run
from make_plots import plot_result_time_series
from web_scrape_price_data import get_preceding_30_days
from datetime import datetime, timedelta
import time


parameters = {
    'name': 'ElectricityArbitrage',
    'generator_name': 'ADK HUDSON___FALLS',
    'date_range': None,
    'num_periods': 24,
    'num_markets': 1,
    'battery_types': {
        'lithium': {
            'size': 1,
            'capacity': 100,
            'charge_loss': 1,
            'max_charge': 50,
            'max_discharge': 100
        },
        'lead': {
            'size': 0.8,
            'capacity': 200,
            'charge_loss': 0.90,
            'max_charge': 25,
            'max_discharge': 50
        },
        'palladium': {
            'size': 2,
            'capacity': 50,
            'charge_loss': 0.85,
            'max_charge': 100,
            'max_discharge': 100
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
start_date = datetime.today()
date_range = get_preceding_30_days(start_date)

parameters['date_range'] = date_range

model, decision_var_dict, model_results, constraint_params = run(parameters, print_results=True)

# plot_result_time_series(model, decision_var_dict, model_results, constraint_params)

# print(decision_var_dict)
print(decision_var_dict['battery_counts'])

for w in range(len( decision_var_dict['warehouses_used'] ) ):
    print( f"Buy Warehouse {w}? - {decision_var_dict['warehouses_used'][w].x }" )

time.sleep(5)

# Plot DVs
plot_result_time_series(model, decision_var_dict, model_results, constraint_params)