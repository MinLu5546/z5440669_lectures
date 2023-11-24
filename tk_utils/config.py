""" Configuration file for the tk_utils package


Includes decorator to inject parameters into doctrings

         
"""
from __future__ import annotations

from tk_utils.api import (
        textwrap,
        pathlib,
        tk_cfg,
        )

from tk_utils._typing import (
        Callable,
        Any,
        TypeVar,
        FuncType,
        Union,
        )


DROPBOX_URL = 'https://www.dropbox.com/scl/fo/x4ehqpmlel1bpak726tfq/h?rlkey=svmnu78zk07umhd82lgi5ub3s&dl=1'

# The PRJDIR should be one level up
TK_PRJDIR = pathlib.Path(tk_cfg.PRJDIR)
PRJDIR = pathlib.Path(__file__).parent.parent


BACKUP_DIR = '_backup'
DBOX_DIR = '_dropbox'
DIRS_TO_EXCL = [
        'venv',
        '.idea',
        BACKUP_DIR,
        #DBOX_DIR,  # bk _dropbox in case they add files
        '__pycache__',
        ]



# used in decorators to preserve the signature of the function it decorates
# see https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
F = TypeVar("F", bound=FuncType)


def _indent(text: str|None, level: int = 1) -> str:
    """ Aux function to indent docstring parameters

    Notes
    -----
    - Adapted from `indent <https://github.com/pandas-dev/pandas/blob/main/pandas/util/_decorators.py>`_
    """
    if not text or not isinstance(text, str):
        return ""
    # First dedent then indent
    if text.startswith('\n'):
        text = textwrap.dedent(text[1:])
    pfix = '    '*level
    text = textwrap.indent(text, pfix)
    # Remove the indentation from the first line
    n = len(pfix)
    return text[n:]

def doc(
        *docstrings: str|Callable, 
        parms: dict,
        indent: int = 1, 
        ) -> Callable[[F], F]:
    """ Recursively input parameter descriptions into docstrings.

    Parameters
    ----------
    *docstrings : str or callable
        The string / docstring / docstring template to be appended in order
        after default docstring under callable.

    parms  dict
        key-value pairs which will be used to format the docstring

    indent : int, optional
        The indentation level (1 = four spaces)

    Notes
    -----
    - Based on `doc decorator <https://github.com/pandas-dev/pandas/blob/main/pandas/util/_decorators.py>`_

    """
    params = {k:_indent(v, indent) for k, v in parms.items()}

    def decorator(decorated: F) -> F:
        # collecting docstring and docstring templates
        docstring_components: list[str | tp.Callable] = []
        if decorated.__doc__:
            docstring_components.append(textwrap.dedent(decorated.__doc__))

        for docstring in docstrings:
            if hasattr(docstring, "_docstring_components"):
                # error: Item "str" of "Union[str, Callable[..., Any]]" has no attribute
                # "_docstring_components"
                # error: Item "function" of "Union[str, Callable[..., Any]]" has no
                # attribute "_docstring_components"
                docstring_components.extend(
                    docstring._docstring_components  # type: ignore[union-attr]
                )
            elif isinstance(docstring, str) or docstring.__doc__:
                docstring_components.append(docstring)

        # Remove indentation of the anchors

        # formatting templates and concatenating docstring
        decorated.__doc__ = "".join(
            [
                component.format(**params)
                if isinstance(component, str)
                else textwrap.dedent(component.__doc__ or "")
                for component in docstring_components
            ]
        )

        # error: "F" has no attribute "_docstring_components"
        decorated._docstring_components = (  # type: ignore[attr-defined]
            docstring_components
        )
        return decorated

    return decorator



