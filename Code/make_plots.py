import numpy as np
import pandas as pd
from datetime import datetime

from web_scrape_price_data import download_price_data, extract_time_series_prices

import plotly.graph_objects as go
import matplotlib.pyplot as plt

def plot_price_time_series(d_date, generator, save_plot=True, aggregation=None):
    if type(d_date) == list and len(d_date) == 2:
        plot_type = 'extended'

        price_df = extract_time_series_prices( d_date, generator,
                    return_df = True, aggregation=aggregation, extended = True)
        date_objs = [ datetime.strptime(d, '%Y%m%d') for d in d_date]
        date_nice_format = date_objs[0].strftime('%Y-%m-%d') + ' to ' + date_objs[1].strftime('%Y-%m-%d')

    elif type(d_date)==str:
        plot_type = 'daily'

        # Ensure data is downloaded
        download_price_data(d_date, generator)
        # Extract time series
        price_df = extract_time_series_prices( d_date, generator,
                    return_df = True, aggregation=aggregation, extended = False)

        date_obj = datetime.strptime(d_date, '%Y%m%d')
        date_nice_format = date_obj.strftime( '%Y-%m-%d' )

    # Create datetime
    price_df['datetime'] = pd.to_datetime(price_df['time'], format='%m/%d/%Y %H:%M:%S')

    # Plot the time series
    agg_string = '' if aggregation is None else f'{aggregation}'

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(price_df['datetime'], price_df['LB_MargPrice'])
    ax.set_xlabel('Time')
    ax.set_ylabel('Price ($/MWh)')
    ax.set_title(f'Price Time Series for {generator} on {date_nice_format} {agg_string}')

    if plot_type == 'daily':
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%I:%M %p'))
    elif plot_type == 'extended':
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%y-%m-%d'))

    if save_plot:
        fig.savefig(f'Figures/price_time_series_{date_nice_format}_{generator}_{agg_string}.png')

    else:
        plt.show()

    return None

def plot_result_time_series(model, decision_var_dict, model_results, constraint_params):
    # Extract data from the dictionary
    buy_ts = model_results['buy_ts']
    sell_ts = model_results['sell_ts']
    prices = constraint_params['prices']
    dates = [datetime.strptime(date, '%m/%d/%Y %H:%M').strftime('%m/%d') for date in constraint_params['price_times']]

    battery_types = set(buy_ts.keys()).union(set(sell_ts.keys()))

    # Create a new time series 'flow_ts' for each battery
    flow_ts = {battery: np.array(buy_ts.get(battery, [0, 0, 0, 0])) - np.array(sell_ts.get(battery, [0, 0, 0, 0]))
            for battery in battery_types}

    # Plot the bar chart for 'flow_ts'
    fig, ax1 = plt.subplots(figsize=(10, 6))
    width = 0.4
    ind = np.arange(len(dates))

    for i, (battery, flow) in enumerate(flow_ts.items()):
        ax1.bar(ind + i * width, flow, width, label=f'{battery} Buy/Sell')

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Buy/Sell Flow')
    date_freq = 75
    ax1.set_xticks(ind[::date_freq])  # Show every couple of days
    ax1.set_xticklabels(dates[::date_freq])
    ax1.legend(loc='upper left')

    # Create a second y-axis for 'prices'
    ax2 = ax1.twinx()
    ax2.plot(ind, prices, color='red', label='Prices')
    ax2.set_ylabel('Prices', color='red')
    ax2.tick_params('y', colors='red')
    ax2.legend(loc='upper right')

    plt.title('Battery Buying/Selling and Prices Over Time')
    plt.show()

    # ---- PLOT TIME SERIES ON ONE GRAPH ---- #


    """ # Plotting both buy_ts and sell_ts on the same graph
    plt.figure(figsize=(10, 6))

    color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    line_styles = ['-', '--']  # Solid line for buy_ts, dashed line for sell_ts

    battery_colors = {} # To store the assigned color for each battery type

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
    plt.show() """

def plot_waterfall_chart(parameters, decision_var_dict, daily_profits):
    descriptions = []
    values = []

    # Get warehosue cost
    descriptions.append('Warehouse Cost')

    num_warehouses = sum(1 for var in decision_var_dict['warehouses_used'].values() if var.x == 1.0)

    for i in range(num_warehouses):
        warehouse_cost = parameters['warehouse_data'][i]['cost']
        values.append(-1*warehouse_cost)

    # Get battery costs
    for b in parameters["battery_counts"].keys() :
        descriptions.append(f'Battery Rental {b}')
        values.append( -1*parameters['battery_counts'][b]*parameters['battery_types'][b]['cost'])

    # Get revenues
    n_days = len(daily_profits)
    for d in range(n_days):
        descriptions.append(f'Revenue {d}')
        values.append( daily_profits[d] )

     # Create waterfall plot
    fig = go.Figure(go.Waterfall(
        x=descriptions,
        y=[ round(v, 2) for v in values ],
        textposition='outside',
        text=[f'${val:,.2f}' for val in values],
        connector={'line': {'color': 'rgb(63, 63, 63)'}},
    ))

    fig.add_shape(
        go.layout.Shape(
            type='line',
            x0=descriptions[0], x1=descriptions[-1],
            y0=0, y1=0,
                line=dict(color='black', width=3)
            )
        )

    # Customize the plot
    fig.update_layout(
        title='Waterfall Plot - Profit Over Time - 1 Month',
        xaxis_title='Costs/Revenues',
        yaxis_title='Cumulative Profit ($)',
    )

    fig.show()