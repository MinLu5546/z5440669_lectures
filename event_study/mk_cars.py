""" mk_cars.py

Utilities to create CARs for the events in our study
"""
import numpy as np
import pandas as pd

import event_study.config as cfg


def mk_cars_df(ret_df, event_df):
    """ Given a data frame with all events of interest for a given ticker
    (`event_df`) and the corresponding data frame with stock and market
    returns (`ret_df`), calculate the Cumulative Abnormal Return over the
    two-day window surrounding each event.

    Parameters
    ----------
    ret_df : pandas dataframe
        Dataframe created by the function `mk_rets.mk_ret_df`. It contains the
        following columns:
            ret : float
                Daily stock return
            mkt : float
                Daily market return
        The index is a DatetimeIndex corresponding to each trading day

    event_df : pandas dataframe
        Dataframe created by the function `mk_events.mk_event_df`. This data
        frame includes all events in our study (uniquely identified by an
        index starting at 1). The columns are:
            firm : str
                The name of the firm issuing the recommendation
            event_date : str
                A string representing the date part of the recommendation,
                formatted as 'YYYY-MM-DD'.
            event_type : str
                A string identifying the event as either an upgrade
                ("upgrade") or downgrade ("downgrade")

    Returns
    -------
    Pandas dataframe
        A data frame with the same format as `event_df` but with an additional
        column containing the CARs:
            car : float
                The CAR for the two-day window surrounding the event

    Notes
    -----
    This function will apply the `mk_cars.calc_car` function to each row of the `event_df`

    """
    cars = event_df.apply(calc_car, axis=1, ret_df=ret_df)
    event_df.loc[:, 'car'] = cars
    return event_df


def calc_car(ser, ret_df, window=2):
    """ For a given row in the dataframe produced by the `mk_event_df` function
    above, compute the cumulative abnormal returns for the event window
    surrounding the event_date by performing the following operations (in this
    order)

    1. Expand the dates using the `expand_dates` function
    2. Join returns in `ret_df`
    3. Sum the abnormal returns to compute the CAR

    Parameters
    ----------
    ser : series
       Series corresponding to a row from the dataframe produced by
        `mk_event_df`

    ret_df : dataframe
        A dataframe with stock and market returns

    Returns
    -------
    float
        Cumulative abnormal return for this row


    """
    # --------------------------------------------------------
    #   Step 4.1: Expand dates and set 'ret_date' as the new index
    # --------------------------------------------------------
    dates = expand_dates(ser, window=window)
    dates.set_index('ret_date', inplace=True)
    # --------------------------------------------------------
    #   Step 4.2: Join stock and market returns returns
    # --------------------------------------------------------
    df = dates.join(ret_df, how='inner')
    # --------------------------------------------------------
    #   Step 4.3: Compute abnormal returns
    # --------------------------------------------------------
    df.loc[:, 'aret'] = df.loc[:, 'ret'] - df.loc[:, 'mkt']
    # --------------------------------------------------------
    #   Step 4.4: Sum abnormal returns
    # --------------------------------------------------------
    # If df is empty, return np.nan
    if len(df) == 0:
        return np.nan
    else:
        return df['aret'].sum()


def expand_dates(ser, window=2):
    """ For a given row in the dataframe produced by the `mk_event_df`
    function above, return a dataframe with the dates for the `window` days
    surrounding the event_date by performing the following operations (in this
    order)

    1. Create a DF with one row for each day in the window ,
        where each row represents a copy of the series in `row`
    2. Create a column called "event_date", which the datetime representation
        of the dates in 'event_date'
    3. Create a column called "event_time" with values from -`window` to `window`
    4. Create another column called "ret_date" with the **datetime**
      representation of the relevant calendar date. The calendar date will be
      the date in "event_date" plus the value from "event_time".

    Parameters
    ----------
    ser : series
       Series corresponding to a row from the dataframe produced by
        `mk_event_df`

    Returns
    -------
    df
        A Pandas dataframe with the following structure:

        - df.index : Integers representing the ID of this event, that is,
            uniquely identifying a unique combination of values (<event_date>,
            <firm>). The index should start at 1.

        - df.columns : See Notes section below

    Notes
    -----

    For instance, suppose window = 2 and consider the following row (an event):


     | event_id | firm       | event_date  |
     |----------+------------+------------|
     | 1        | Wunderlich | 2012-02-16 |


     This function would produce the following data:


     | firm       | event_date | event_time | ret_date   |
     |------------+------------+------------+------------|
     | Wunderlich | 2012-02-16 | -2         | 2012-02-14 |
     | Wunderlich | 2012-02-16 | -1         | 2012-02-15 |
     | Wunderlich | 2012-02-16 | 0          | 2012-02-16 |
     | Wunderlich | 2012-02-16 | 1          | 2012-02-17 |
     | Wunderlich | 2012-02-16 | 2          | 2012-02-18 |

     which should be stored in a dataframe with the following characteristics:

     ----------------------------------------------
     Data columns (total 4 columns):
      #   Column      Non-Null Count  Dtype
     ---  ------      --------------  -----
      0   firm        5 non-null      object
      1   event_date  5 non-null      datetime64[ns]
      2   event_time  5 non-null      int64
      3   ret_date    5 non-null      datetime64[ns]
     ----------------------------------------------


    """
    # Create a list of series
    row_lst = [ser] * (2 * window + 1)

    # Create a new dataframe with copies of the single-row dataframe
    df = pd.concat(row_lst, axis=1).transpose()

    # Create the event date col
    df['event_date'] = pd.to_datetime(df.loc[:, 'event_date'])
    # Create the event time
    df.loc[:, 'event_time'] = [i for i in range(-window, window + 1)]

    # Create the return date
    df.loc[:, 'ret_date'] = df.event_date + pd.to_timedelta(df.event_time, unit='day')

    # keep only relevant columns
    cols = ['firm', 'event_date', 'event_time', 'ret_date']
    df = df.loc[:, cols]

    # rename the index
    df.index.name = 'event_id'
    return df


def _test_mk_cars_df(sample_only=False):
    """  Will test the function mk_cars_df
    Parameters
    ----------
    sample_only : bool, optional
        If True, will use a single event from the `event_df`

    Notes
    -----
    if `sample_only` is True, the event df will become:

        | event_id | event_date | event_type | car       |
        |----------|------------|------------|-----------|
        | 1        | 2020-09-23 | upgrade    | $CAR_{1}$ |


    """
    from event_study import mk_rets, mk_events

    def _mk_example_event_df(event_df):
        """ Creates an event df to be used if sample_only is True
        """
        cond = (event_df.event_date == '2020-09-23') & (event_df.firm == 'DEUTSCHE BANK')
        # The slice is so it returns a DF (not a series)
        event_df = event_df.loc[cond]
        event_df.index = [1]
        event_df.index.name = 'event_id'
        return event_df

    # Create the `ret_df` and the `event_df` data frames
    tic = 'TSLA'
    ret_df = mk_rets.mk_ret_df(tic)
    event_df = mk_events.mk_event_df(tic)

    # Sample only?
    if sample_only is True:
        event_df = _mk_example_event_df(event_df)
        ret_df = ret_df.loc['2020-09-21':'2020-09-25']

    print('-----------------------------')
    print(' event_df:')
    print('-----------------------------')
    print(event_df)
    print('')

    print('-----------------------------')
    print(' ret_df:')
    print('-----------------------------')
    print(ret_df)
    print('')

    # Create the CAR df
    cars_df = mk_cars_df(ret_df=ret_df, event_df=event_df)

    print('-----------------------------')
    print(' cars_df:')
    print('-----------------------------')
    print(cars_df)


if __name__ == "__main__":
    sample_only = True
    _test_mk_cars_df(sample_only)