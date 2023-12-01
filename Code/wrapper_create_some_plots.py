from make_plots import plot_price_time_series
from web_scrape_price_data import download_price_data, extract_time_series_prices


# Plot extended time series for ADK HUDSON FALLS
d_dates = ['20231101', '20231130']
generator_name = 'ADK HUDSON___FALLS'
plot_price_time_series( d_dates, generator_name, save_plot = True, aggregation = 'hourly')

# Plot single day for Hudson Falls
plot_price_time_series( '20231128', generator_name, save_plot = True, aggregation = 'hourly')