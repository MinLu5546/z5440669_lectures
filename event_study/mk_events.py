""" mk_events.py

Utilities to create events from recommendations
"""
import pandas as pd

import event_study.config as cfg


#   Functions to process recommendations into events
def mk_event_df(tic):
    """ Subsets and processes recommendations given a ticker and return a data
    frame with all events in the sample.

    Parameters
    ----------
    tic : str
        Ticker

    Returns
    -------
    pandas dataframe

        The columns are:
        * event_date : string
            Date string with format 'YYYY-MM-DD'
        * firm : string
            Name of the firm (upper case)
        * event_type : string
            Either "downgrade" or "upgrade"

        index: integer
            Index named 'event_id' starting at 1

    Notes
    -----
    This function will perform the following actions:

    1. Read the appropriate CSV file with recommendations into a data frame
    2. Create variables identifying the firm and the event date
    3. Deal with multiple recommendations
    4. Create a table with all relevant events

    """

    # ------------------------------------------------------------------------
    # Step 1. Read the appropriate CSV file with recommendations into a data
    # frame
    # ------------------------------------------------------------------------
    # Read the source file, set the column 'Date' as a DatetimeIndex
    pth = cfg.csv_locs(tic)['rec_csv']
    df = pd.read_csv(pth, index_col='Date', parse_dates=['Date'])

    # Standardise column names and keep only the columns of interest
    cols = ['firm', 'action']
    df = cfg.standardise_colnames(df)[cols]

    # ------------------------------------------------------------------------
    # Step 2. Create variables identifying the firm and the event date
    # ------------------------------------------------------------------------
    # Replace the values of the column "firm" with their upper case version
    # Alternative: df.loc[:, 'firm'] = [x.upper() for x in df.loc[:, 'firm']]
    df.loc[:, 'firm'] = df.loc[:, 'firm'].str.upper()

    # The column 'firm' is already part of the source data, so we only need to
    # create the 'event_date' column
    df.loc[:, 'event_date'] = df.index.strftime('%Y-%m-%d')

    # ------------------------------------------------------------------------
    # Step 3. Deal with multiple recommendations
    # ------------------------------------------------------------------------
    df.sort_index(inplace=True)
    groups = df.groupby(['event_date', 'firm'])
    # Select the last obs for each group using the GroupBy method `last`
    # Note: result is a dataframe with a multi-index. The reset_index will convert
    # these indexes to columns
    df = groups.last().reset_index()

    # ------------------------------------------------------------------------
    # Step 4. Create a table with all relevant events
    # ------------------------------------------------------------------------
    # 4.1: Subset the "action" column
    # Note: Either one of these statements will create the boolean series:
    #   cond = (df['action'] == 'up') | (df['action'] == 'down')
    #   cond = df.loc[:, 'action'].str.contains('up|down')
    cond = df.loc[:, 'action'].str.contains('up|down')
    df = df.loc[cond]

    # 4.2: Create a column with the event type ("downgrade" or "upgrade")
    # We will create an intermediary function to illustrate the use of the
    # series method `apply`
    def _mk_et(value):
        """ Converts the string `value` as follows:
            - "down" --> "downgrade"
            - "up" --> "upgrade"
        and raise an exception if value is not "up" or "down"
        """
        if value == 'down':
            return 'downgrade'
        elif value == 'up':
            return 'upgrade'
        else:
            raise Exception(f'Unknown value for column `action`: {value}')

    df.loc[:, 'event_type'] = df['action'].apply(_mk_et)

    # 4.3 Create the event id index:
    #   - Reset the index so it becomes 0, 1, ...
    #   - Add 1 to the index
    #   - Name the index 'event_id' for future reference
    df.reset_index(inplace=True)
    df.index = df.index + 1
    df.index.name = 'event_id'

    # 4.4: Reorganise the columns
    cols = ['firm', 'event_date', 'event_type']
    df = df[cols]

    return df


if __name__ == "__main__":
    tic = 'TSLA'
    df = mk_event_df(tic)
    print(df)
    df.info()
