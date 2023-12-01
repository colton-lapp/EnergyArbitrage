import os
import re
import time
import numpy as np
import pandas as pd
import gurobipy as gp
import sys
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def extract_date(file_path):
    match = re.match(r'^(\d+)', file_path.split('/')[4])

    return match.group(1)

def download_price_data(download_date, generator_name):

    print("\n\nDownloading price data...\n", '-'*70, sep='')

    if download_date == None:
        download_date = datetime.today()
        download_date = download_date.strftime("%Y%m%d")

    dates = [download_date]

    # Remove any dates where the file already exists
    for date in dates:
        if os.path.exists(f'Data/prices_{date}_{generator_name}.csv'):
            print(f'...Price data already downloaded for date: {date}, Generator: {generator_name}')
            dates.remove(date)

    if len(dates) != 0:
        driver_path = ChromeDriverManager().install()

        home_dir = os.path.expanduser("~")

        download_directory = os.path.join(home_dir, 'Downloads_CSV')
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': download_directory}
        chrome_options.add_experimental_option('prefs', prefs)

        # Initialize the driver, use try except blocks depending on version of selenium installed
        try:
            # Older selenium version that takes executable path as argument
            driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        except:
            try:
                # For selenium version 3.141.0 or above
                driver=webdriver.Chrome(options=chrome_options)
            except:
                sys.exit("Please install correct version of selenium")

        driver.get('http://mis.nyiso.com/public/P-24Blist.htm')
        all_links = driver.find_elements("xpath", "//a[@href]")

        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        for date in dates:
            for link in all_links:
                href = link.get_attribute('href')

                if ('csv' in href) and (date in href):
                    link.click()
                    time.sleep(2)
                    break

        csv_files = [file for file in os.listdir(download_directory) if file.endswith('.csv')]

        for file_name in csv_files:
            file_path = os.path.join(download_directory, file_name)
            d_date = extract_date(file_path)
            price_df = pd.read_csv(file_path)

            price_df = price_df[price_df['Name'] == generator_name][['Time Stamp'
                                                                , 'LBMP ($/MWHr)'
                                                                , 'Marginal Cost Losses ($/MWHr)'
                                                                , 'Marginal Cost Congestion ($/MWHr)']].reset_index(drop=True)
            
            price_df = price_df.rename(columns={ 'Time Stamp': 'time'
                                                , 'LBMP ($/MWHr)': 'LB_MargPrice'
                                                , 'Marginal Cost Losses ($/MWHr)': 'MargCostLosses'
                                                , 'Marginal Cost Congestion ($/MWHr)': 'MargCostCongestion'}
                                        )

            # Save dfs in data dir
            print(f'Saving price data for date: {d_date}, Generator: {generator_name}')
            price_df.to_csv(f'Data/prices_{date}_{generator_name}.csv', index=False)

        driver.quit()
    
    print("\n -- Price data downloaded successfully! -- \n\n")

    


def extract_time_series_prices( data_date, generator, return_df = False, aggregation = None):

    if data_date == None:
        data_date = datetime.today()
        data_date = data_date.strftime("%Y%m%d")

    prices_df = pd.read_csv(f'Data/prices_{data_date}_{generator}.csv')

    # Ensure that the prices are in order
    prices_df = prices_df.sort_values(by='time').reset_index(drop=True)

    if return_df:
        return prices_df
        
    # Extract the prices
    times = prices_df['time'].values
    prices = prices_df['LB_MargPrice'].values
    marg_cost_loss = prices_df['MargCostLosses'].values
    marg_cost_cong = prices_df['MargCostCongestion'].values

    # Perform any temporal aggregations ?
    if aggregation is not None:
        pass

    return { 'times': times
            , 'prices': prices
            , 'marg_cost_loss': marg_cost_loss
            , 'marg_cost_cong': marg_cost_cong 
            }

