import os
import re
import sys
import time
import shutil
import zipfile
import requests
import numpy as np
import pandas as pd
import gurobipy as gp
from selenium import webdriver
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager

columns = ['Time Stamp', 'LBMP ($/MWHr)', 'Marginal Cost Losses ($/MWHr)', 'Marginal Cost Congestion ($/MWHr)']
new_columns = {
    'Time Stamp': 'time',
    'LBMP ($/MWHr)': 'LB_MargPrice',
    'Marginal Cost Losses ($/MWHr)': 'MargCostLosses',
    'Marginal Cost Congestion ($/MWHr)': 'MargCostCongestion'
}

home_dir = os.path.expanduser("~")
download_directory = os.path.join(home_dir, 'Downloads_CSV')
storage_directory = 'Data'

def extract_date(file_path):
    match = re.match(r'^(\d+)', file_path.split('/')[4])

    return match.group(1)

def extract_name(file_path):
    parts = file_path.split('/')

    return parts[6]

def get_preceding_30_days(input_date):
    date_list = []

    # Generate dates for that day and the preceding 30 days
    for i in range(31, 0, -1):
        # Subtract a day from the date in each iteration
        prev_date = input_date - timedelta(days=i)
        date_list.append(prev_date.strftime("%Y%m%d"))

    return date_list

def download_price_data(date_range, generator_name):
    print("\n\nDownloading price data...\n", '-'*70, sep='')

    if date_range == None:
        download_date = datetime.today()
        download_date = download_date.strftime("%Y%m%d")

        date_range = [download_date]

    # Create list of dates to download
    dates_to_download = []
    for date in date_range:
        if os.path.exists(f'{storage_directory}/{date}_{generator_name}.csv'):
            print(f'...Price data already downloaded for date: {date}, Generator: {generator_name}')
        else:
            dates_to_download.append(date)

    if len(dates_to_download) != 0:
        driver_path = ChromeDriverManager().install()

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

        driver.get('http://mis.nyiso.com/public/P-2Blist.htm')
        all_links = driver.find_elements("xpath", "//a[@href]")

        if not os.path.exists(download_directory):
            os.makedirs(download_directory)

        for date in dates_to_download:
            found = False
            i = 0

            if os.path.exists(f'{storage_directory}/{date}damlbmp_gen.csv'):
                print(f'...Price data already downloaded for date: {date}')
                found = True

            while (not found) and (i < len(all_links)):
                link = all_links[i]
                href = link.get_attribute('href')

                if ('csv' in href) and (date in href) and ('zip' not in href) and ('realtime' not in href):
                    link.click()
                    time.sleep(3)

                    print(download_directory)

                    file_name = extract_name(href)
                    destination_path = f'{storage_directory}/{file_name}'

                    if not os.path.exists(destination_path):
                        source_path = f'{download_directory}/{file_name}'

                        # Move the file using shutil.move()
                        shutil.move(source_path, destination_path)

                    found = True

                i += 1

            if not found:
                year_month = date[0:6]
                zip_url = f'http://mis.nyiso.com/public/csv/damlbmp/{year_month}01damlbmp_gen_csv.zip'
                response = requests.get(zip_url, timeout=10)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Save the zip file to the destination folder

                    #with open(os.path.join(download_directory, "month.zip"), "wb") as zip_file:
                    with open(os.path.join(storage_directory, "month.zip"), "wb") as zip_file:
                        zip_file.write(response.content)

                    # Extract the downloaded zip file
                    #with zipfile.ZipFile(os.path.join(download_directory, "month.zip"), 'r') as zip_ref:
                    with zipfile.ZipFile(os.path.join(storage_directory, "month.zip"), 'r') as zip_ref:
                       #zip_ref.extractall(download_directory)
                        zip_ref.extractall(storage_directory)

                    # Remove the downloaded zip file
                    #os.remove(os.path.join(download_directory, "month.zip"))
                    os.remove(os.path.join(storage_directory, "month.zip"))
                else:
                    print("Failed to download the zip file")

        # csv_files = [file for file in os.listdir(storage_directory) if file.endswith('.csv')]

        driver.quit()

        for date in date_range:
            file_path = f'{storage_directory}/{date}_{generator_name}.csv'

            if not os.path.exists(file_path):
                price_df = pd.read_csv(f'{storage_directory}/{date}damlbmp_gen.csv')

                price_df = price_df[price_df['Name'] == generator_name][columns].reset_index(drop=True)
                price_df = price_df.rename(columns=new_columns)

                # Save dfs in data dir
                print(f'Saving price data for date: {date}, Generator: {generator_name}')
                price_df.to_csv(f'{storage_directory}/{date}_{generator_name}.csv', index=False)

    print("\n -- Price data downloaded successfully! -- \n\n")


def extract_time_series_prices(date_range, generator, return_df=False, aggregation=None, extended=False):
    result = None

    dfs = []

    for date in date_range:
        if extended:
            prices_df = pd.read_csv(f'{storage_directory}/extended_time_series/{date[0]}_{date[1]}_{generator}.csv')
        else:
            prices_df = pd.read_csv(f'{storage_directory}/{date}_{generator}.csv')

        dfs.append(prices_df)

    prices_df = pd.concat(dfs)

    # Ensure that the prices are in order
    prices_df = prices_df.sort_values(by='time').reset_index(drop=True)

    # Perform any temporal aggregations ?
    # if aggregation == 'hourly':
    #     # Convert the 'timestamp' column to datetime
    #     prices_df['datetime'] = pd.to_datetime(prices_df['time'])

    #     # Set the 'timestamp' column as the index
    #     prices_df.set_index('datetime', inplace=True)

    #     # Resample the DataFrame to hourly frequency and aggregate using the mean
    #     hourly_marg_prices = prices_df[['LB_MargPrice']].resample('H').mean()
    #     hourly_marg_cost_loss = prices_df[['MargCostLosses']].resample('H').mean()
    #     hourly_marg_cost_cong = prices_df[['MargCostCongestion']].resample('H').mean()

    #     #Concat
    #     hourly_df = pd.concat([hourly_marg_prices, hourly_marg_cost_loss, hourly_marg_cost_cong], axis=1)

    #     # Reset the index to include the timestamp as a column
    #     hourly_df = hourly_df.reset_index()
    #     hourly_df.rename(columns={'datetime': 'time'}, inplace=True)
    #     prices_df = hourly_df

    if return_df:
        result = prices_df
    else:
        # Extract the prices
        times = prices_df['time'].values
        prices = prices_df['LB_MargPrice'].values
        marg_cost_loss = prices_df['MargCostLosses'].values
        marg_cost_cong = prices_df['MargCostCongestion'].values

        result = {
            'times': times,
            'prices': prices,
            'marg_cost_loss': marg_cost_loss,
            'marg_cost_cong': marg_cost_cong
        }

    return result


def create_extended_time_series(start_date, end_date, generator_name, aggregation=None):
    result = None

    # Check if already done:
    if os.path.exists(f'{storage_directory}/extended_time_series/{start_date}_{end_date}_{generator_name}.csv'):
        print(f'Extended time series already created for dates:\
            {start_date} to {end_date}, Generator: {generator_name}')
        # Read in and return df
        result = pd.read_csv(f'{storage_directory}/extended_time_series/{start_date}_{end_date}_{generator_name}.csv')
    else:
        # create list of dates between start_date and end_date inclusive
        date_list = pd.date_range(start=start_date, end=end_date).tolist()

        full_df = None

        for date in date_list:
            print("Fetching price data for date: ", date)
            date_formatted = date.strftime("%Y%m%d")

            # Try to read it in from data dir
            if os.path.exists(f'{storage_directory}/{date_formatted}_{generator_name}.csv'):
                price_df = pd.read_csv(f'{storage_directory}/{date_formatted}_{generator_name}.csv')

                # Concat it to full_df
                if full_df is None:
                    full_df = price_df
                else:
                    full_df = pd.concat([full_df, price_df], axis=0)

            # Try to read it in from downloads
            if os.path.exists(f'{storage_directory}/downloads/{date_formatted}realtime_gen.csv'):
                price_df = pd.read_csv(f'{storage_directory}/downloads/{date_formatted}realtime_gen.csv')
                price_df = price_df[price_df['Name'] == generator_name][columns].reset_index(drop=True)

                price_df = price_df.rename(columns=new_columns)

                price_df.to_csv(f'{storage_directory}/{date_formatted}_{generator_name}.csv', index=False)

                # Concat it to full_df
                if full_df is None:
                    full_df = price_df
                else:
                    full_df = pd.concat([full_df, price_df], axis=0)

        # Save extended time series
        result = full_df.to_csv(f'Data/extended_time_series/{start_date}_{end_date}_{generator_name}.csv', index=False)

    return result


