import matplotlib.pyplot as plt
import pandas as pd
from web_scrape_price_data import download_price_data, extract_time_series_prices
from datetime import datetime

def plot_price_time_series( d_date, generator, save_plot = True, aggregation = None):

    # if d_date is a list of two dates, this is extended time series

    if type(d_date) == list and len(d_date) == 2:
        plot_type = 'extended'

        price_df = extract_time_series_prices( d_date, generator, 
                    return_df = True, aggregation=aggregation, extended = True)
        date_objs = [ datetime.strptime(d, '%Y%m%d') for d in d_date]
        date_nice_format = date_objs[0].strftime( '%Y-%m-%d' ) + ' to ' + date_objs[1].strftime( '%Y-%m-%d' )

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