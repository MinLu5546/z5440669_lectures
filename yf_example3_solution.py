""" yf_example3_solution.py

Utilities to download daily stock prices for Qantas for a given year into
CSV files
"""

import os

import toolkit_config as cfg
import yf_example2


def qan_prc_to_csv(year):
    """ Download stock prices from Yahoo Finance for a given year into
    CSV file. This file will be located under the `cfg.DATADIR` folder and
    will be called "qan_prc_YYYY.csv`, where 'YYYY' corresponds to the year
    `year`.

    Parameters
    ----------
    year : int
        An integer with a four-digit year
    """
    tic = 'QAN.AX'
    start=f'{year}-01-01'
    end=f'{year}-12-31'
    pth = os.path.join(cfg.DATADIR, f'qan_prc_{year}.csv')
    df = yf_example2.yf_prc_to_csv(
            tic=tic,
            pth=pth,
            start=start,
            end=end)

if __name__ == "__main__":
    year = 2020
    qan_prc_to_csv(year)