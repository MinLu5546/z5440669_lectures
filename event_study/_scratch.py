""" config.py

Configuration file for the event_study package
"""
import os

import toolkit_config as tk_cfg

# --------------------------------------------------------
#   Constants
# --------------------------------------------------------
DATADIR = tk_cfg.DATADIR
FF_FACTORS_CSV = os.path.join(DATADIR, 'ff_daily.csv')
START = '1900-01-01'
END = '2020-12-31'


# --------------------------------------------------------
#   Location of the `<prc csv>` and `<rec csv>` files
# --------------------------------------------------------
def csv_locs(tic):
    """ Returns a dictionary with the location of the source CSV files for a
    given ticker `tic`.

    Parameters
    ----------
    tic : str
        Ticker

    Returns
    -------
    dict
        A dictionary with the following keys:
        'rec_csv': The complete path to the CSV with the recommendation data
        'prc_csv': The complete path to the CSV with the price data
    """
    tic = tic.lower().replace('.', '_')
    rec_csv = os.path.join(DATADIR, f'{tic}_rec.csv')
    prc_csv = os.path.join(DATADIR, f'{tic}_prc.csv')
    return {
        'rec_csv': rec_csv,
        'prc_csv': prc_csv,
    }


# --------------------------------------------------------
#   Aux function to process col names
# --------------------------------------------------------
def standardise_colnames(df):
    """ Renames the columns in `df` so that
    - Names are lower case
    - Spaces are replaced with '_'

    Parameters
    ----------
    df : dataframe

    Notes
    -----
    - If column with the standardised name already exists, the new column will
      include a '_' prefix
    """
    cols = set(df.columns)

    # You can define `local` functions
    def _parse_name(colname):
        # Processes the column name
        new_name = colname.lower().replace(' ', '_')
        # Decide what to do. The options are:
        # 1) column name is already properly formatted:
        #   => do nothing
        # 2) column name is not properly formatted but exists in the dataframe
        #   => Include '_' prefix
        # 3) Else: return formatted name
        if new_name == colname:
            # Returns original column
            return colname
        elif new_name in cols:
            return '_' + new_name
        else:
            return new_name

    return df.rename(columns=_parse_name)