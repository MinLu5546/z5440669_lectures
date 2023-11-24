""" 
"""
import inspect
import sys

from tk_utils._tk_utils import (
        backup,
        sync_dbox,
        update,
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


# Get all the functions imported above
_funcs = [
        backup,
        sync_dbox,
        csv_to_fobj,
        csv_to_df,
        pprint,
        ]


def _func_doc(func, name_only: bool = False):
    # Returns the documentation for a function
    sig = inspect.signature(func)
    #fname = f"\033[4m{func.__name__}{sig}\033[0m"
    fname = colorize(f"{func.__name__}{sig}", 'green')
    if name_only is True:
        return fname
    else:
        docstring = func.__doc__.strip()
        return f"""{fname}: 
        
    {docstring}
    """


_func_desc = '\n'.join([_func_doc(x) for x in _funcs])

_func_list = '\n'.join([f" {_func_doc(x, name_only=True)}" for x in _funcs])

_func_header = colorize("Functions", 'green')

__doc__ = f""" The `tk_utils` package. 

IMPORTANT: This folder should be placed directly under your toolkit project
folder:

    toolkit/   
    | ...
    |__ tk_utils/           <- This folder
    |__ toolkit_config.py   <- Your config file (REQUIRED)

IMPORTANT: This module is should not be modified. Also, it includes Python
concepts/libraries we did not (and will not) discuss in this course. Please
use this module "as is" and do not worry about the implementation.

IMPORTANT: This module requires a correctly configured `toolkit_config.py`
module.  If you followed the instructions in Lecture 4.4, you are all set!

This module implements the following functions:

{_func_list}

Each function is documented below:

{_func_header}
---------

{_func_desc}


"""

