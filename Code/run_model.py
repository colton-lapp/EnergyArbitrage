import gurobipy as gp
from gurobipy import GRB
from webdriver_manager.chrome import ChromeDriverManager

from web_scrape_price_data import download_price_data, extract_time_series_prices

# OPTIGUIDE DATA CODE GOES HERE

# Main function
def create_model(parameters):
    name = parameters['name']
    generator_name = parameters['generator_name']
    date_range = parameters['date_range']
    battery_types = parameters['battery_types']
    battery_types_used = parameters['battery_types_used']
    battery_counts = parameters['battery_counts']
    warehouse_data = parameters['warehouse_data']
    warehouses_used = parameters['warehouses_used']
    carry_over = parameters['carry_over']

    # Container to fill with prices and dates to pass out of the function
    constraint_params = {}

    download_price_data(date_range, generator_name)

    # Extract time series of prices in a list for Gurobi
    prices_dict = extract_time_series_prices(date_range, generator_name, aggregation=None)
    price_times = prices_dict['times']

    prices = prices_dict['prices']

    # Create the model
    model = gp.Model(name)

    num_periods = len(prices)
    parameters['num_periods'] = num_periods

    periods = range(num_periods)

    decision_var_dict = {}

    # Create storage of battery data if one wasn't passed in
    if battery_counts is None:
        decision_var_dict['battery_counts'] = {}

    # Create the main decision vars - amount to buy and sell for each period
    for battery_type in battery_types_used:
        for key in [f'{battery_type}_buy', f'{battery_type}_sell']:
            decision_var_dict[key] = model.addVars(num_periods, vtype=GRB.CONTINUOUS, name=key, lb=0)

    objs = []
    total_area_needed = 0

    # Create constraints
    for battery_type in battery_types_used:
        battery = battery_types[battery_type]

        # Extract data about the batteries from the parameters
        buy = decision_var_dict[f'{battery_type}_buy']
        sell = decision_var_dict[f'{battery_type}_sell']
        capacity = battery['capacity']
        charge_loss = battery['charge_loss']
        max_charge = battery['max_charge']
        max_discharge = battery['max_discharge']
        size = battery['size']
        cost = battery['cost']

        # Create decison vars for the batteries if they weren't passed in
        if battery_counts is None:
            battery_count = model.addVar(vtype=GRB.INTEGER, name=f'Number of {battery_type} batteries', lb=0)
            decision_var_dict['battery_counts'][battery_type] = battery_count

            objs.append(cost * battery_count * -1)
        else:
            battery_count = battery_counts[battery_type]

        # Main contraints
        for p in range(num_periods):
            current_level = gp.quicksum(charge_loss * buy[p_] - sell[p_] for p_ in range(p + 1))

            if not carry_over and p % 24 == 0:
                model.addConstr(current_level <= 0, 'CarryOverConstraint')

            model.addConstr(current_level <= capacity * battery_count, f'CapacityConstraint_period_{p+1}') # Can't have more charge than max capacity
            model.addConstr(current_level >= 0, f'SupplyConstraint_period_{p+1}') # Can't have a negative amount of charge
            model.addConstr(buy[p] * charge_loss <= max_charge * battery_count, f'ChargeConstraint_period_{p+1}') # Can't charge more then the batteries can charge in one period
            model.addConstr(sell[p] <= max_discharge * battery_count, f'DischargeConstraint_period_{p+1}') # Can't discharge more then the batteries can charge in one period

        model.update()

        # Objective value summation
        objs = objs + [prices[p] * sell[p] - prices[p] * buy[p] for p in periods]

        total_area_needed += battery_count * size

    # Create decision vars for warehouses if not passed in
    if warehouses_used is None:
        warehouses_used = model.addVars(len(warehouse_data), vtype=GRB.BINARY, name=f'Number of warehouses')
        decision_var_dict['warehouses_used'] = warehouses_used

        model.update()

        model.addConstr(
            gp.quicksum(
                warehouse_data[i]['area'] * warehouses_used[i] for i, warehouse in enumerate(warehouse_data)
            ) >= total_area_needed,
            name='Area_constraint'
        )

        objs = objs + [warehouse_data[i]['cost'] * warehouses_used[i] * -1 for i, warehouse in enumerate(warehouse_data)]

    model.update()

    model.setObjective(
        gp.quicksum(objs),
        GRB.MAXIMIZE
    )

    # OPTIGUIDE CONSTRAINT CODE GOES HERE

    constraint_params['price_times'] = price_times
    constraint_params['prices'] = prices_dict['prices']

    return [model, decision_var_dict, constraint_params]


# Run the model
def run(parameters, print_results=False):
    battery_types_used = parameters['battery_types_used']

    # Create model
    [model, decision_var_dict, constraint_params] = create_model(parameters)

    # Run model
    model.optimize()

    if model.status == GRB.OPTIMAL:
        # Unpack results
        model_results = {}

        model_results['num_periods'] = parameters['num_periods']
        model_results['buy_ts'] = {battery_type: [] for battery_type in battery_types_used}
        model_results['sell_ts'] = {battery_type: [] for battery_type in battery_types_used}
        model_results['time'] = list(range(parameters['num_periods']))
        model_results['total_profit'] = model.objVal

        if print_results:
            print("\nOptimal Solution:")

        for p in range(model_results['num_periods']):
            if print_results:
                print(f"\nPeriod {p + 1}:")

            for battery_type in battery_types_used:
                buy = decision_var_dict[f'{battery_type}_buy']
                sell = decision_var_dict[f'{battery_type}_sell']

                if print_results:
                    print(f"\nFor Battery Type: {battery_type}:")

                if print_results:
                    print(f"Buy {buy[p].x}")
                    print(f"Sell {sell[p].x}")

                model_results['buy_ts'][battery_type].append(buy[p].x)
                model_results['sell_ts'][battery_type].append(sell[p].x)

        if print_results:
            print(f"\nTotal Profit: {model.objVal}")

    else:
        model_results = None
        print("No solution found")

    if parameters['battery_counts'] is None:
        decision_var_dict['battery_counts'] = {key: battery_count.x for key, battery_count in decision_var_dict['battery_counts'].items()}

    return [model, decision_var_dict, model_results, constraint_params]