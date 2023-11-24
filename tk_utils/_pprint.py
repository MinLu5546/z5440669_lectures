""" Pretty printer
"""
from __future__ import annotations

import pprint as _pp

from tk_utils.api import (
        io,
        textwrap,
        csv,
        dc,
        pd,
        )

from tk_utils.config import (
        doc,
        )


_PP_PARMS = {
    'pretty': '''
    pretty : bool, optional
        If True, use pprint.pformat as a print formatter. Otherwise, use str()
        Defaults to True
    ''',
    'indent': '''
    indent: str, optional 
        Indentation to be added.
        Defaults to '' (no indentation)
    ''',
    'show_type': '''
    show_type : bool, optional
        If True, pretty print will also display the object type.
        Defaults to True
    ''',
    'df_info': '''
    df_info : bool, optional
        If True and object is a pandas data frame, call the `info` method
        Defaults to False
    ''',
    'width': '''
    width : int, optional
        Parameter `width` to be passed to pretty printer. Ignored if `pretty`
        is False.
        Defaults to 40
    ''',
    'sort_dicts': '''
    sort_dicts : bool, optional
        Parameter `sort_dicts` to be passed to the pretty printer. 
        Defaults to False
    ''',
    'df_max_cols': '''
    df_max_cols: int, optional
        Number of data frame columns to display. 
        Defaults to None (all columns)
    ''',
    'df_max_rows': '''
    df_max_rows: int, optional
        Number of data frame rows to display
        Defaults to None (all columns)
    ''',
    'as_string': '''
    as_string : bool, optional
        If True, returns a string instead of writing to standard output.
        Defaults to True
    ''',
    'sep': '''
    sep: bool, optional
        If True, includes a message separator
        Defaults to False
    ''',
    }


# ----------------------------------------------------------------------------
#   ANSI escape codes
#   [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
# ----------------------------------------------------------------------------
COLORS = {
    #   Colors 
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'FOREST': '\033[96m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'PURPLE': '\033[95m',
    #  Formats
    'BOLD': '\033[1m',
    'UNDERLINED': '\033[4m',
    'NORMAL': '\033[0m',
    }

def colorize(text, color):
    """ Returns a colorized text

    Parameters
    ----------
    text : str
        String to be formatted

    color : text
        the name of the color or format (NOT case sensitive).
        Valid values are:
            'BLUE'
            'GREEN'
            'FOREST'
            'YELLOW'
            'RED'
            'PURPLE'
            'BOLD'
            'UNDERLINED'
            'NORMAL'

    """
    ucolor = color.upper()
    if ucolor not in COLORS:
        valid = ','.join(COLORS.keys())
        raise Exception(f"Parameter color must be one of {valid}")
    start = COLORS[ucolor]
    end = COLORS['NORMAL']
    return f'{start}{text}{end}'

# Auxiliary classes
@doc(indent=1, parms=_PP_PARMS)
@dc.dataclass
class _PPrintCfg:
    """ Configuration object with default parameter values

    Parameters
    ----------
    {pretty}
    {indent}
    {show_type}
    {df_info}
    {df_max_cols}
    {df_max_rows}
    {width}
    {sort_dicts}
    {as_string}
    {sep}

    """
    pretty: bool = True
    indent: str = ''
    show_type: bool = True
    df_info: bool = False
    df_max_cols: int|None = None
    df_max_rows: int|None = None
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
            index: int|None = None,
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


@doc(indent=1, parms=_PP_PARMS)
def pprint(obj: object,
           msg: str|None = None, 
           **kargs):
    """ Pretty prints `obj`. If object is a string, print it as is.

    NOTE: Will ignore str instances with value '?'

    Parameters
    ----------
    obj : any object 

    msg : str, optional
        Message preceding obj representation.
        Defaults to None.

    **kargs
        Overrides the default pretty print parameters (stored in
        lec_utils.pp_cfg):

    {pretty}
    {indent}
    {show_type}
    {df_info}
    {df_max_cols}
    {df_max_rows}
    {width}
    {sort_dicts}
    {as_string}
    {sep}


    Usage
    -----

    >> import tk_utils

    To create a DF from a CSV-formatted string (not file):

    >>  cnts = '''
        date       , ticker , Some rets
        2020-03-23 , aapl   , 0.0043158473975633
        2020-03-24 , aapl   , 0.0069854151404052
        '''
    >> df = tk_utils.csv_to_df(cnts)
    >> print(df)

                 date ticker  Some rets
        0  2020-03-23   aapl   0.004316
        1  2020-03-24   aapl   0.006985

    To pretty print an object use the `pprint` function. For instance, using the
    `df` created above:

    >> tk_utils.pprint(df, sep=True, show_type=True)

        ----------------------------------------
                 date ticker  Some rets
        0  2020-03-23   aapl   0.004316
        1  2020-03-24   aapl   0.006985

        Object type is <class 'pandas.core.frame.DataFrame'>
        ----------------------------------------


    Default parameters for the `pprint` function are stored in the `pp_cfg` object
    
    >> print(tk_utils.pp_cfg)
    
        _PPrintCfg({{'pretty': True,
         'indent': '',
         'show_type': True,
         'df_info': False,
         'df_max_cols': None,
         'df_max_rows': None,
         'width': 40,
         'sort_dicts': False,
         'as_string': False,
         'sep': False}})
    
    
    The default parameters can be modified. For instance, separator
    lines are not included in the output of `tk_utils.pprint` by default. To
    change this behavior set the parameter `sep` to True:
    
    >> tk_utils.pprint(df)         # sep = False by default
    
                 date ticker  Some rets
        0  2020-03-23   aapl   0.004316
        1  2020-03-24   aapl   0.006985
    
    
    >> tk_utils.pp_cfg.sep = True  # Change the default to True
    
    >> tk_utils.pprint(df)         # sep = False by default
    
        ----------------------------------------
                 date ticker  Some rets
        0  2020-03-23   aapl   0.004316
        1  2020-03-24   aapl   0.006985
        ----------------------------------------


        
    """

    # Ignore '?'
    if isinstance(obj, str) and obj == '?':
        return None

    # Initialize objects
    opts = pp_cfg._copy(**kargs)

    lines = _Lines()
    _sep = '-'*opts.width

    if opts.sep is True:
        lines.add(_sep)

    # Add msg and str representation of the obj
    if msg is not None:
        if not msg.endswith('\n'):
            msg += '\n'
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

