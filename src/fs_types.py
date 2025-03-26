from collections import namedtuple
from decimal import Decimal
from fractions import Fraction
from typing import Union, Any, cast, Self, Callable
from enum import Enum

AlphaType = Union[float, Decimal, Fraction]
Numeric = Union[int, AlphaType]
BorderType = list[Numeric] | tuple[Numeric, ...] | Numeric

SaB = namedtuple("SaB", ["Side", "Coord"])

class BorderSide(Enum):
    LEFT = "left"
    RIGHT= "right"

class Alpha:
    """
    :param value: membership level between 0 and 1.
    """
    def __init__(self, value: AlphaType, small_check: bool = False):
        self._value: AlphaType = value
        self._small_check: bool = small_check
        self._type_check()

    def _type_check(self):
        if not isinstance(self.value, AlphaType):
            raise TypeError(f"Alpha value must be a float, Decimal or Fraction, not {type(self.value)}")
        if not self.small_check and not (0 <= self.value <= 1):
            raise ValueError(f"Alpha-cut level must be between 0 and 1. Given value: {self.value}")

    @property
    def value(self) -> AlphaType:
        return self._value

    @property
    def small_check(self) -> bool:
        return self._small_check

    @small_check.setter
    def small_check(self, small_check: bool):
        self._small_check = small_check
        self._type_check()

    def check_and_get_type(self, other) -> type:
        rettype = type(other.value)
        if not isinstance(self.value, rettype):
            raise TypeError(f"Alphas has another types {type(self.value)} and {type(other.value)}. ")
        return rettype

    def check_and_do_given_operation(self, other: "Alpha", operation: Callable, error_message: str) -> Self:
        if not isinstance(other, Alpha):
            raise TypeError(f"You can't make operation on Alpha and {type(other)} class")
        oper1 = self.value
        oper2 = other.value
        if not isinstance(oper1, type(oper2)):
            raise TypeError(f"Alphas has another types {type(self.value)} and {type(other.value)}. {error_message}")
        else:
            return Alpha(operation(oper1, oper2), True)

    def __add__(self, other: "Alpha") -> Self:
        return self.check_and_do_given_operation(other,
                                                 lambda a, b: a + b,
                                                 f"Cannot add {other} to {self}.")

    def __sub__(self, other: "Alpha") -> Self:
        return self.check_and_do_given_operation(other,
                                                 lambda a, b: a - b,
                                                 f"Cannot subtract {other} to {self}.")

    def __mul__(self, other: "Alpha") -> Self:
        return self.check_and_do_given_operation(other,
                                                 lambda a, b: a * b,
                                                 f"Cannot multiply {other} to {self}.")

    def __truediv__(self, other: "Alpha") -> Self:
        if other.value == 0:
            raise ValueError("Cannot divide by 0")
        return self.check_and_do_given_operation(other,
                                                 lambda a, b: a / b,
                                                 f"Cannot divide {other} to {self}.")

    def __pow__(self, other: "Alpha") -> Self:
        return self.check_and_do_given_operation(other,
                                                 lambda a, b: a ** b,
                                                 f"Cannot raise {other} to {self}.")

    def __eq__(self, other: Any) -> bool:
        """
        :param other: another Alpha membership object.
        :return: True if alpha levels are the same.
        """
        if not isinstance(other, Alpha):
            return False
        try:
            self.check_and_get_type(other)
        except TypeError as e:
            raise TypeError(f"Cannot compare {other} to {self}. {e}")
        return self.value == other.value

    def __repr__(self) -> str:
        return f"Alpha({self.value})"

    def __str__(self) -> str:
        return self.__repr__()

    def __lt__(self, other: "Alpha") -> bool:
        return self.value < other.value

    def __gt__(self, other: "Alpha") -> bool:
        return self.value > other.value

    def __hash__(self) -> int:
        return hash(self.value)

class Border:
    def __init__(self, border: BorderType, covered: bool = False, side: BorderSide | None = None) -> None:
        self._set_border(border)
        self._covered = covered
        self._side = side
        self._dtrial = self._border[0]
        self._check()

    def _set_border(self, border: BorderType) -> None:
        if isinstance(border, Numeric):
            self._border = (border,)
        elif isinstance(border, tuple | list):
            if len(border) == 0:
                raise ValueError("border cannot be empty")
            self._border = tuple(border)
        else:
            raise TypeError(f"border must be of type BorderType, not {type(border)}")


    def _check(self) -> None:
        if not isinstance(self._dtrial, Numeric):
            raise TypeError(f"Border must be of type Numeric, not {type(self._dtrial)}")
        if not all(isinstance(elem, type(self._dtrial)) for elem in self._border):
            raise TypeError(f"All elements of border must be the same type")
        if any(last >= nxt for last, nxt in zip(self._border[:-1], self._border[1:])):
            self._covered = True

    def __repr__(self) -> str:
        return f"Border({self._border})"

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return len(self._border)

    @property
    def side(self) -> BorderSide | None:
        return self._side

    @side.setter
    def side(self, side: BorderSide | None) -> None:
        self._side = side

    def get_sab_list(self) -> list[SaB]:
        if self.side is None:
            raise TypeError("Cannot get sab list from None side value")
        return [SaB(self.side, border) for border in self._border]

    @property
    def covered(self) -> bool:
        """
        :return: covered flag.
        """
        return self._covered

    @property
    def dtrial(self) -> Numeric:
        """
        :return: datatype of borders.
        """
        return self._dtrial

    @property
    def borders(self) -> tuple[Numeric, ...]:
        """
        :return: values of borders.
        """
        return self._border

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Border):
            return False
        return self.borders == other.borders


    @staticmethod
    def are_left_right(left: 'Border', right: 'Border') -> None:
        if type(left.dtrial) != type(right.dtrial):
            raise TypeError(f"Borders must have the same data type")
        if len(left) != len(right):
            raise ValueError(f"Borders must have the same length")
        if not all(l <= r for l, r in zip(left.borders, right.borders)):
            raise ValueError(f"Alpha_cut length cant be negative")
        if not all(left >= right for left, right in zip(left.borders[1:], right.borders[:-1])):
            raise ValueError("Two parts of alpha-cut can't cover.")
        if left.covered or right.covered:
            raise ValueError(f"Borders must be not covered to be borders of fuzzy-set. Use uncover class-method")

    @classmethod
    def uncover(cls, left: 'Border', right: 'Border') -> tuple['Border', 'Border']:
        if len(left) != len(right):
            raise ValueError(f"Borders must have same length")
        op_list = []
        op_list.extend(left.get_sab_list())
        op_list.extend(right.get_sab_list())
        op_list.sort(key = lambda x: x.Coord)
        numerator = 0
        new_left = []
        new_right = []
        for sab in op_list:
            if sab.Side == BorderSide.LEFT:
                numerator += 1
                if numerator == 1:
                    new_left.append(sab.Coord)
            if sab.Side == BorderSide.RIGHT:
                numerator -= 1
                if numerator == 0:
                    new_right.append(sab.Coord)
            if numerator < 0:
                raise ValueError(f"Improper borders. Some alpha-cut ends before start!")
        return Border(new_left, side=BorderSide.LEFT), Border(new_right, side=BorderSide.RIGHT)


    def __add__(self, other: 'Border') -> Self:
        cast_to = type(self.dtrial)
        if not isinstance(other.dtrial, cast_to):
            raise TypeError(f"To add borders must have the same data type")
        def convert(value1, value2) -> Numeric:
            if cast_to is Decimal:
                return Decimal(value1) + Decimal(value2)
            elif cast_to is Fraction:
                return Fraction(value1) + Fraction(value2)
            elif cast_to is float:
                return float(value1) + float(value2)
            else:
                return int(value1) + int(value2)

        result: list[Numeric] = cast(list[Numeric],
                    [convert(sborder, oborder)
                    for sborder in self.borders
                    for oborder in other.borders])
        return Border(result, True)

    def __sub__(self, other: 'Border') -> Self:
        cast_to = type(self.dtrial)
        if not isinstance(other.dtrial, cast_to):
            raise TypeError(f"To subtract borders must have the same data type")
        def convert(value1, value2) -> Numeric:
            if cast_to is Decimal:
                return Decimal(value1) - Decimal(value2)
            elif cast_to is Fraction:
                return Fraction(value1) - Fraction(value2)
            elif cast_to is float:
                return float(value1) - float(value2)
            else:
                return int(value1) - int(value2)

        result: list[Numeric] = cast(list[Numeric],
                    [convert(sborder, oborder)
                    for sborder in self.borders
                    for oborder in other.borders])
        return Border(result, True)

    def __mul__(self, other: 'Border') -> Self:
        cast_to = type(self.dtrial)
        if not isinstance(other.dtrial, cast_to):
            raise TypeError(f"To multiplied borders must have the same data type")
        if len(other.borders) != 1 and len(self.borders) != 1:
            raise ValueError(f"You can't multiply by Border with more than one border")
        def convert(value1, value2) -> Numeric:
            if cast_to is Decimal:
                return Decimal(value1) * Decimal(value2)
            elif cast_to is Fraction:
                return Fraction(value1) * Fraction(value2)
            elif cast_to is float:
                return float(value1) * float(value2)
            else:
                return int(value1) * int(value2)

        result: list[Numeric] = cast(list[Numeric],
                    [convert(sborder, oborder)
                    for sborder in self.borders
                    for oborder in other.borders])
        return Border(result, True)
