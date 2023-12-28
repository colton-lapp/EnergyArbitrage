from run_model import run
from web_scrape_price_data import get_preceding_30_days
from datetime import datetime, timedelta

# Get battery numbers
def stage_one(start_date, parameters):
    date_range = get_preceding_30_days(start_date)
    parameters['date_range'] = date_range

    return run(parameters)

def stage_two(start_date, parameters, decision_var_dict):
    parameters['battery_counts'] = decision_var_dict['battery_counts']
    parameters['warehouses_used'] = 'set'
    parameters['date_range'] = [start_date.strftime("%Y%m%d")]

    daily_profits = []
    start_date = datetime.today() - timedelta(days=1)

    for start_date in get_preceding_30_days(start_date):
        parameters['date_range'] = [start_date]

        [model, _, _, _] = run(parameters)

        daily_profits.append(model.objVal)

    return daily_profits
