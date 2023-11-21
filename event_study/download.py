""" download.py

Utilities to download data from Yahoo Finance
"""
import yfinance as yf

from event_study import config as cfg


# --------------------------------------------------------
#   Function to download recommendations
# --------------------------------------------------------
def yf_rec_to_csv(tic, pth,
                  start=None,
                  end=None):
    """ Downloads analysts recommendation from Yahoo Finance and saves the
    information in a CSV file

    Parameters
    ----------
    tic : str
        Ticker

    pth : str
        Location of the output CSV file

    start: str, optional
        Download start date string (YYYY-MM-DD)
        If None (the default), start is set to '1900-01-01'

    end: str, optional
        Download end date string (YYYY-MM-DD)
        If None (the default), end is set to the most current date available
    """
    c = yf.Ticker(tic)
    c.history(start=start, end=end).tz_localize(None)
    # Make sure we only relevant dates
    if start is not None and end is not None:
        df = c.recommendations.loc[start:end]
    elif start is not None:
        df = c.recommendations.loc[start:]
    elif end is not None:
        df = c.recommendations.loc[:end]
    else:
        df = c.recommendations
    df.to_csv(pth)


def get_data(tic):
    """ Downloads price and recommendation data for a given ticker `tic`
    given the sample period defined by the `config` variables `START` and
    `END`.

    Parameters
    ----------
    tic : str
        Ticker

    """
    # Get output paths
    locs = cfg.csv_locs(tic)

    # Download and save prices
    print(f'Downloading prices for {tic}...')
    df = yf.download(tic,
            start=cfg.START,
            end=cfg.END,
            ignore_tz=True
            )
    pth = locs['prc_csv']
    df.to_csv(pth)
    print('Done')

    # Download and save recs
    print(f'Downloading recs for {tic}...')
    yf_rec_to_csv(tic,
            pth=locs['rec_csv'],
            start=cfg.START,
            end=cfg.END)
    print('Done')


if __name__ == "__main__":
    get_data('tsla')