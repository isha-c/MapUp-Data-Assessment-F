import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    distance_matrix = pd.pivot_table(df, values='distance', index='id_start', columns='id_end', fill_value=0)
    for col in distance_matrix.columns:
        for row in distance_matrix.index:
            if row != col:
                route1 = distance_matrix.at[row, col]
                route2 = distance_matrix.at[col, row]
                total_distance = route1 + route2
                distance_matrix.at[row, col] = distance_matrix.at[col, row] = total_distance


    return distance_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    unrolled_df = distance_matrix.stack().reset_index()
    unrolled_df.columns = ['id_start', 'id_end', 'distance']
    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']].reset_index(drop=True)

    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    avg_distance_reference = df[df['id_start'] == reference_id]['distance'].mean()
    threshold = 0.1 * avg_distance_reference

    ids_within_threshold = df.groupby('id_start')['distance'].mean()
    ids_within_threshold = ids_within_threshold[ (avg_distance_reference - threshold <= ids_within_threshold) &
        (ids_within_threshold <= avg_distance_reference + threshold)].reset_index()

    return ids_within_threshold


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    toll_rates = {
        'moto': 0.8,
        'car': 1.2,
        'rv': 1.5,
        'bus': 2.2,
        'truck': 3.6
    }

    for vehicle_type, rate in toll_rates.items():
        df[vehicle_type] = df['distance'] * rate


    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
    weekday_discounts = {
        (0, 0, 0, 10, 0, 0): 0.8,
        (10, 0, 0, 18, 0, 0): 1.2,
        (18, 0, 0, 23, 59, 59): 0.8
    }

    weekend_discount = 0.7

    df['start_day'] = df['end_day'] = df['start_time'] = df['end_time'] = None

    for index, row in df.iterrows():
        start_day, end_day = row['id_start'].split('_')[1], row['id_end'].split('_')[1]
        start_time, end_time = map(int, row['id_start'].split('_')[0].split(':')), map(int, row['id_end'].split('_')[0].split(':'))
        
        df.at[index, 'start_day'] = start_day
        df.at[index, 'end_day'] = end_day
        df.at[index, 'start_time'] = start_time
        df.at[index, 'end_time'] = end_time

        is_weekend = start_day in ['Saturday', 'Sunday']
        for time_range, discount_factor in weekday_discounts.items():
            if not is_weekend and (
                time_range[0] <= start_time[0] < time_range[3] or
                (time_range[0] == start_time[0] and time_range[1] <= start_time[1] < time_range[4]) or
                (time_range[1] == start_time[1] and time_range[2] <= start_time[2] <= time_range[5])):
                df.at[index, 'car'] *= discount_factor

        if is_weekend:
            df.at[index, 'car'] *= weekend_discount

    return df
