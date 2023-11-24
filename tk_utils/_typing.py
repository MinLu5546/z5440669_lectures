""" Types

"""
# :mod: tk_utils.typing.py
from __future__ import annotations

from collections.abc import (
        MutableMapping,
        Iterable,
        MutableSequence,
        )
from typing import (
        Any,
        Callable,
        TypeVar,
        Union,
        TextIO,
        )

# used in decorators to preserve the signature of the function it decorates
# see https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
FuncType = Callable[..., Any]

