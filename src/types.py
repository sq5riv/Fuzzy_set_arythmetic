from decimal import Decimal
from fractions import Fraction
from typing import Union, Any, cast, Self, Callable, NamedTuple
from enum import Enum

AlphaType = Union[float, Decimal, Fraction]
Numeric = Union[int, AlphaType]
BorderType = list[Numeric] | tuple[Numeric, ...] | Numeric


class BorderSide(Enum):
    LEFT = "left"
    RIGHT = "right"
    INSIDE = "inside"


class SaB(NamedTuple):
    side: BorderSide
    coord: Numeric


class Alcs(NamedTuple):
    alpha_level: float
    coord: float
    side: BorderSide
