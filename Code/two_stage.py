from run_model import run
from web_scrape_price_data import get_preceding_30_days
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

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
        {'area': 100, 'cost': 100},
        {'area': 100, 'cost': 120},
        {'area': 100, 'cost': 150},
        {'area': 100, 'cost': 200},
        {'area': 100, 'cost': 500}
    ]
}

# Get warehouse and battery numbers
start_date = datetime.today()
date_range = get_preceding_30_days(start_date)

parameters['date_range'] = date_range


model, decision_var_dict, model_results, constraint_params = run(parameters, print_results=True)

print(decision_var_dict['warehouses_used'])


constraint_params['dates']  = [datetime.strptime(date, '%m/%d/%Y %H:%M') for date in constraint_params['price_times']]

# ---- PLOT TIME SERIES ON ONE GRAPH ---- #


""" # Plotting both buy_ts and sell_ts on the same graph
plt.figure(figsize=(10, 6))

color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
line_styles = ['-', '--']  # Solid line for buy_ts, dashed line for sell_ts

battery_colors = {}  # To store the assigned color for each battery type

for action, line_style in zip(['buy_ts', 'sell_ts'], line_styles):
    for battery, time_series in model_results[action].items():
        if battery not in battery_colors:
            battery_colors[battery] = color_cycle[len(battery_colors) % len(color_cycle)]

        plt.plot(time_series, label=f'{action.capitalize()}: {battery}', linestyle=line_style,
                 color=battery_colors[battery])

plt.title('Buy and Sell Time Series for Batteries')
plt.xlabel('Time')
plt.ylabel('Value')
plt.legend()
plt.show()
 """


# ---- PLOT TIME SERIES ON TWO GRAPHS ---- #
# Extract unique battery names
all_batteries = set(model_results['buy_ts'].keys()).union(model_results['sell_ts'].keys())

# Create subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Plotting buy_ts
for battery in all_batteries:
    time_series = model_results['buy_ts'].get(battery, [])
    ax1.plot(constraint_params['dates'], time_series, label=f'Buy: {battery}', linestyle='-')

ax1.set_title('Buy Time Series for Batteries')
ax1.set_ylabel('Value')
ax1.legend()

# Plotting sell_ts
for battery in all_batteries:
    time_series = model_results['sell_ts'].get(battery, [])
    ax2.plot(constraint_params['dates'], time_series, label=f'Sell: {battery}', linestyle='--')

ax2.set_title('Sell Time Series for Batteries')
ax2.set_ylabel('Value')
ax2.legend()

# Plotting prices
ax3.plot(constraint_params['dates'], constraint_params['prices'], label='Prices', linestyle='-', color='purple')

ax3.set_title('Prices')
ax3.set_xlabel('Time')
ax3.set_ylabel('Value')
ax3.legend()

date_format = DateFormatter("%m-%d")
for ax in [ax1, ax2, ax3]:
    ax.xaxis.set_major_formatter(date_format)
    ax.xaxis_date()  # Treat x-axis as dates

# Adjust layout
plt.tight_layout()
plt.show()