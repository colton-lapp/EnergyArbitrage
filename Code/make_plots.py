import matplotlib.pyplot as plt
import pandas as pd
from web_scrape_price_data import download_price_data, extract_time_series_prices
from datetime import datetime

def plot_price_time_series(d_date, generator, save_plot = True, aggregation = None):

    # if d_date is a list of two dates, this is extended time series

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
    constraint_params['dates']  = [datetime.strptime(date, '%m/%d/%Y %H:%M') for date in constraint_params['price_times']]

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