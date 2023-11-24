""" CSV utils

Includes functions to convert string formatted as CSV to file objects and DF

         
"""

from tk_utils.api import (
        csv, 
        io,
        pd,
        )


def csv_to_fobj(cnts, strip: bool = True) -> io.StringIO:
    """ Given a string mimicking the contents of a CSV file, 
    returns an object that behaves like a CSV file when passed to 
    the pandas.read_csv function

    All extra spaces are removed.

    IMPORTANT: Once the fake csv file is read using the read_csv method, all
    its contents will disappear (because pandas will reach the end of the
    file). You must always create a new fake csv file before using it as a
    parameter of `read_csv` (or any other similar function).
    

    Parameters
    ----------
    cnts : str
        Contents similar to what you would find in the original CSV file

    Returns
    -------
    io.StringIO

    Example
    -------

    >> import tk_utils

    >> cnts = '''
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
    >> sio = tk_utilscsv_to_fobj(cnts)

    """
    # Initial strip
    cnts = cnts.strip()

    # Format the contents of the CSV 
    reader = csv.reader(io.StringIO(cnts))

    output = io.StringIO()
    writer = csv.writer(output)

    for line in reader:
        if strip is True:
            line = [x.strip(' ') for x in line]
        writer.writerow(line)
    output.seek(0)
    return output


def csv_to_df(cnts: str, *args, **kargs) -> pd.DataFrame:
    """ Given a string mimicking the contents of a CSV File, this function 
    will return a data frame as if using pandas.read_data frame

    Parameters
    ----------
    cnts : str
        A CSV-formatted string with data (e.g., a string with the contents
        of a CSV file). All whites paces will be ignored.

    *args, **kargs will be passed to pandas.read_csv

    Returns
    -------
    data frame

    Example
    -------

    >> import tk_utils

    >> cnts = '''
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
    >> df = tk_utils.csv_to_df(cnts)

    """
    fake_csv = csv_to_fobj(cnts)
    df = pd.read_csv(fake_csv, *args, **kargs)
    return df


