""" lec_utils.py

Lecture utilities

This module includes three functions we will use when completing the scaffold
codes during class:

    lec_utils.pprint: Pretty prints objects
    lec_utils.csv_to_df: Construct DFs from CSV formatted strings
    lec_utils.csv_to_fobj: Creates a "file object" from a CSV formatted string

The implementation of these functions is not part of the course and will not
be discussed.

This module should be placed alongside the other "slides" codes

    toolkit/
    |   ...
    |__ webinars/
    |   |__ __init__.py             <- Required (empty file)
    |   |__ lec_utils.py            <- this module
    |   |__ week8_slides_p1.py
    |   |__ week8_slides_p2.py
    |       ...
    |__ toolkit_config.py


Usage
-----
This module can then be imported by any other module under `toolkit`

>> from webinars import lec_utils

To create a DF from a CSV-formatted string (not file):

>>  cnts = '''
    date       , ticker , Some rets
    2020-03-23 , aapl   , 0.0043158473975633
    2020-03-24 , aapl   , 0.0069854151404052
    '''
>> df = lec_utils.csv_to_df(cnts)
>> print(df)

             date ticker  Some rets
    0  2020-03-23   aapl   0.004316
    1  2020-03-24   aapl   0.006985

To pretty print an object use the `pprint` function. For instance, using the
`df` created above:

>> lec_utils.pprint(df, sep=True, show_type=True)

    ----------------------------------------
             date ticker  Some rets
    0  2020-03-23   aapl   0.004316
    1  2020-03-24   aapl   0.006985

    Object type is <class 'pandas.core.frame.DataFrame'>
    ----------------------------------------


Default parameters for the `pprint` function are stored in the `pp_cfg` object

>> print(lec_utils.pp_cfg)

    _PPrintCfg({'pretty': True,
     'indent': '',
     'show_type': True,
     'df_info': False,
     'df_max_cols': None,
     'df_max_rows': None,
     'width': 40,
     'sort_dicts': False,
     'as_string': False,
     'sep': False})


The default parameters can be modified. For instance, separator
lines are not included in the output of `lec_utils.pprint` by default. To
change this behavior set the parameter `sep` to True:

>> lec_utils.pprint(df)         # sep = False by default

             date ticker  Some rets
    0  2020-03-23   aapl   0.004316
    1  2020-03-24   aapl   0.006985


>> lec_utils.pp_cfg.sep = True  # Change the default to True

>> lec_utils.pprint(df)         # sep = False by default

    ----------------------------------------
             date ticker  Some rets
    0  2020-03-23   aapl   0.004316
    1  2020-03-24   aapl   0.006985
    ----------------------------------------

"""
# IMPORTANT: Please do not modify this module
# IMPORTANT: The implementation of the functions/classes defined in this
# module is NOT part of the course and will not be discussed.
from __future__ import annotations

import io
import textwrap
import csv
import dataclasses as dc
import pprint as _pp

import pandas as pd

_PP_PARMS = f'''
    pretty : bool, optional
        If True, use pprint.pformat as a print formatter. Otherwise, use str()
        Defaults to True

    indent: str, optional 
        Indentation to be added.
        Defaults to '' (no indentation)

    show_type : bool, optional
        If True, pretty print will also display the object type.
        Defaults to True

    df_info : bool, optional
        If True and object is a pandas data frame, call the `info` method
        Defaults to False

    width : int, optional
        Parameter `width` to be passed to pretty printer. Ignored if `pretty`
        is False.
        Defaults to 40

    sort_dicts : bool, optional
        Parameter `sort_dicts` to be passed to the pretty printer. 
        Defaults to False

    df_max_cols: int, optional
        Number of data frame columns to display. 
        Defaults to None (all columns)

    df_max_rows: int, optional
        Number of data frame rows to display
        Defaults to None (all columns)

    as_string : bool, optional
        If True, returns a string instead of writing to standard output.
        Defaults to True

    sep: bool, optional
        If True, includes a message separator
        Defaults to False

'''


# Auxiliary classes
@dc.dataclass
class _PPrintCfg:
    """ Configuration object with default parameter values

    Parameters
    ----------
    {pp_parms}

    """
    __doc__ = __doc__.format(pp_parms=_PP_PARMS)
    pretty: bool = True
    indent: str = ''
    show_type: bool = True
    df_info: bool = False
    df_max_cols: int | None = None
    df_max_rows: int | None = None
    width: int = 40
    sort_dicts: bool = False
    as_string: str = False
    sep: bool = False

    def __str__(self):
        if self.pretty is True:
            s = _pp.pformat(self._asdict(), **self._pp_kargs())
            return f"{self.__class__.__name__}({s})"
        else:
            return str(self)

    def _asdict(self):
        return dc.asdict(self)

    def _copy(self, **kargs):
        """ Returns a copy of the instance, optionally replacing parameters
        with values in `kargs`
        """
        return dc.replace(self, **kargs)

    def _pp_kargs(self):
        """ Returns arguments to be passed to pprint.pformat as a dict
        """
        return {
            'width': self.width,
            'sort_dicts': self.sort_dicts,
        }

    def update(self, **kargs):
        for k, v in kargs.items():
            setattr(self, k, v)


pp_cfg = _PPrintCfg()


class _Lines(list):
    """ Lines to be printed
    """

    def add(self,
            line: str,
            strip: bool = False,
            bold: bool = False,
            index: int | None = None,
            ):
        """ Adds a formatted element to the list

        Parameters
        ----------
        line : str
            The line to add
        strip : bool
            If True, strip the line first
            Defaults to False
        bold : bool
            If True, line (and separators) will be printed in bold
            Defaults to False
        index : int, optional
            If None, append the element to the end of the list,
            otherwise, insert
            Defaults to None
        """
        elem = line if strip is False else line.strip()
        if bold is True:
            elem = f"\033[1m{elem}\033[0m"
        if index is None:
            self.append(elem)
        else:
            self.insert(index, elem)


def _get_df_info(df):
    """ Returns a string with the contents of df.info()

    Parameters
    ----------
    df : data frame

    Returns
    -------
    str
        A string with the output of `df.info()`

    """
    _stdout = io.StringIO()
    df.info(buf=_stdout)
    return _stdout.getvalue()


def _obj_as_str(obj, **kargs):
    """ Returns the string representation of an object
    """
    opts = pp_cfg._copy(**kargs)

    # String representing the object
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        _kargs = {
            'max_rows': opts.df_max_rows,
        }
        if isinstance(obj, pd.DataFrame):
            _kargs['max_cols'] = opts.df_max_cols
        else:
            _kargs.update({
                'name': False if opts.as_string is True else True,
                'dtype': False if opts.as_string is True else True,
            })
        return obj.to_string(**_kargs)
    elif isinstance(obj, str):
        return obj
    else:
        if opts.pretty is True:
            return _pp.pformat(obj, **opts._pp_kargs())
        else:
            return str(obj)


def pprint(obj: object,
           msg: str | None = None,
           **kargs):
    """ Pretty prints `obj`. If object is a string, print it as is.

    Parameters
    ----------
    obj : any object

    msg : str, optional
        Message preceding obj representation.
        Defaults to None.

    **kargs
        Overrides the default pretty print parameters (stored in
        lec_utils.pp_cfg):
    {pp_parms}


    """
    # Initialize objects
    opts = pp_cfg._copy(**kargs)

    lines = _Lines()
    _sep = '-' * opts.width

    if opts.sep is True:
        lines.add(_sep)

    # Add msg and str representation of the obj
    if msg is not None:
        lines.add(_obj_as_str(msg, **kargs))
    lines.add(_obj_as_str(obj, **kargs))

    # Add other info

    # df info
    if isinstance(obj, pd.DataFrame) and opts.df_info is True:
        lines.add('')
        s = _get_df_info(obj)
        lines.extend(s.splitlines())

    elif opts.show_type is True:
        lines.add('')
        lines.add(_obj_as_str(f"Object type is {type(obj)}", **kargs))

    if opts.sep is True:
        lines.add(_sep)

    # Final string
    output = '\n'.join(f"{opts.indent}{x}" for x in lines)

    if opts.as_string is True:
        return output
    else:
        print(output)


_pp_parms = '\n'.join(f'    {x}' for x in _PP_PARMS.splitlines())
pprint.__doc__ = pprint.__doc__.format(pp_parms=_pp_parms)


def csv_to_fobj(cnts, strip: bool = True):
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
    >> sio = csv_to_fobj(cnts)

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


def csv_to_df(cnts: str, *args, **kargs):
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
    >> df = csv_to_df(cnts)

    """
    fake_csv = csv_to_fobj(cnts)
    df = pd.read_csv(fake_csv, *args, **kargs)
    return df


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


def _test():
    """ Run all test functions
    """
    _test_csv_to_fobj()
    _test_csv_to_df()
    _test_pprint()


# ----------------------------------------------------------------------------
#   test
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # _test()
    pass
