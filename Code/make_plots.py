import matplotlib.pyplot as plt
import pandas as pd
from web_scrape_price_data import download_price_data, extract_time_series_prices
from datetime import datetime

def plot_price_time_series( d_date, generator, save_plot = True):

    # Ensure data is downloaded
    download_price_data(d_date, generator)

    # Extract time series 
    price_df = extract_time_series_prices( d_date, generator, return_df = True)

    # Create datetime
    price_df['datetime'] = pd.to_datetime(price_df['time'], format='%m/%d/%Y %H:%M:%S')

    # Plot the time series
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(price_df['datetime'], price_df['LB_MargPrice'])
    ax.set_xlabel('Time')
    ax.set_ylabel('Price ($/MWh)')
    date_obj = datetime.strptime(d_date, '%Y%d%m') ; date_nice_format = date_obj.strftime( '%Y-%m-%d' )
    ax.set_title(f'Price Time Series for {generator} on {date_nice_format}')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%I:%M %p'))
    

    if save_plot:
        fig.savefig(f'Figures/price_time_series_{d_date}_{generator}.png')

    else:
        plt.show()

    return None