""" Tests
"""

from tk_utils.api import (
        pd,
        )


from tk_utils._tk_utils import (
        backup,
        sync_dbox,
        )

from tk_utils._csv import (
        csv_to_fobj,
        csv_to_df,
        )

from tk_utils._pprint import (
        pprint,
        pp_cfg,
        colorize,
        )





def _test_csv_to_fobj():
    """ Test function for csv_to_fobj
    """
    cnts = '''
    date       , ticker , Some rets
    2020-03-23 , aapl   , 0.0043158473975633
    2020-03-24 , aapl   , 0.0069854151404052
    '''
    fobj = csv_to_fobj(cnts)
    df = pd.read_csv(fobj, index_col='date', parse_dates=['date'])
    print(df)
    df.info()
    print(df.columns)


def _test_csv_to_df():
    """ Test function for csv_to_df
    """
    cnts = '''
    date       , ticker , Some rets
    2020-03-23 , aapl   , 0.0043158473975633
    2020-03-24 , aapl   , 0.0069854151404052
    '''
    df = csv_to_df(cnts)



def _get_test_df():
    """ Returns a test data frame
    """
    cnts = '''
        date       , ticker , aret
        2020-03-23 , aapl   , 0.0043158473975633
        2020-03-24 , aapl   , 0.0069854151404052
        2020-03-25 , aapl   , -0.0172487870335345
        2020-03-26 , aapl   , -0.0075169454085904
        2020-03-27 , aapl   , -0.0065422952313599
        2020-09-21 , aapl   , 0.0411257704573225
        2020-09-22 , aapl   , 0.0055157543092731
        2020-09-23 , aapl   , -0.0171460038923635
        2020-09-24 , aapl   , 0.0077687759117516
        2020-09-25 , aapl   , 0.0203160884172309
        2020-06-10 , tsla   , 0.095301976146737
        2020-06-11 , tsla   , 0.0081658913098732
        2020-06-12 , tsla   , -0.0515085773206743
        2020-09-21 , tsla   , 0.0271745806895752
        2020-09-22 , tsla   , -0.0661870109303436
        2020-09-23 , tsla   , -0.0786109433530374
        2020-09-24 , tsla   , 0.0170341872949434
        2020-09-25 , tsla   , 0.0332138512137659
        2020-12-01 , tsla   , 0.0204326196578375
        2020-12-02 , tsla   , -0.0283590501662298
        2020-12-03 , tsla   , 0.0413770986293646
        2020-12-04 , tsla   , -0.000661469719309
        '''
    df = csv_to_df(cnts)
    return df

def _test_pprint():
    """
    """
    df = _get_test_df()
    pprint(df, df_info=True, sep=True, df_max_rows=10, df_max_cols=2)


def main():
    """ Run all test functions
    """
    _test_csv_to_fobj()
    _test_csv_to_df()
    _test_pprint()


    





