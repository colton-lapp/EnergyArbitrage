from run_model import run
from web_scrape_price_data import get_preceding_30_days
from datetime import datetime, timedelta

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
            'charge_loss': 0.95,
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
            'charge_loss': 0.95,
            'max_charge': 150,
            'max_discharge': 200
        }
    },
    'battery_types_used': ['lithium', 'lead', 'palladium'],
    'warehouse_data': [
        {'area': 100, 'cost': 1.0},
        {'area': 100, 'cost': 1.2},
        {'area': 100, 'cost': 1.5},
        {'area': 100, 'cost': 2.0},
        {'area': 100, 'cost': 5.0}
    ]
}

# Get warehouse and battery numbers
start_date = datetime.today()
date_range = get_preceding_30_days(start_date)

parameters['date_range'] = date_range

[model, decision_var_dict] = run(parameters, print_results=True)

print(decision_var_dict['warehouses_used'])
