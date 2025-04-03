from decimal import Decimal
from fractions import Fraction
from typing import Any, Self, cast

from fuzzy_set_arythmetic.types import BorderType, Numeric, SaB, BorderSide


class Border:
    """
    Border class describes alpha-cut borders. In this package approach alpha-cut is set of sections.
    """
    def __init__(self, border: BorderType, covered: bool = False, side: "BorderSide | None" = None) -> None:
        self._set_border(border)
        self._covered = covered
        self._side = side
        self._dtrial = self._border[0]
        self._check()

    def __repr__(self) -> str:
        return f"Border({self._border})"

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return len(self._border)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Border):
            return False
        return self.borders == other.borders

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

    def _check(self) -> None:
        if not isinstance(self._dtrial, Numeric):
            raise TypeError(f"Border must be of type Numeric, not {type(self._dtrial)}")
        if not all(isinstance(elem, type(self._dtrial)) for elem in self._border):
            raise TypeError(f"All elements of border must be the same type")
        if any(last >= nxt for last, nxt in zip(self._border[:-1], self._border[1:])):
            self._covered = True

    def _set_border(self, border: BorderType) -> None:
        if isinstance(border, Numeric):
            self._border = (border,)
        elif isinstance(border, tuple | list):
            if len(border) == 0:
                raise ValueError("border cannot be empty")
            self._border = tuple(border)
        else:
            raise TypeError(f"border must be of type BorderType, not {type(border)}")

    @property
    def side(self) -> "BorderSide | None":
        """
        :return: BorderSide (Left, Right or Inside (for plot)) or None if it's not.
        """
        return self._side

    @side.setter
    def side(self, side: "BorderSide | None") -> None:
        """
        :param side: BorderSide or None.
        """
        self._side = side

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


    def get_sab_list(self) -> list[SaB]:
        """
        :return: Returns SaB - BorderSide and Border coord list.
        """
        if self.side is None:
            raise TypeError("Cannot get sab list from None side value")
        return [SaB(self.side, border) for border in self._border]


    @classmethod
    def uncover(cls, left: 'Border', right: 'Border') -> tuple['Border', 'Border']:
        """
        Method to uncover Borders. While adding or subtracting AlphaCuts borders can be covered.
        Covered borders means, any point of domain is covered more than one by AlphaCut.

        :param left: Border Object with LEFT BorderSide.
        :param right: Border Object with RIGHT BorderSide.
        :return: Returns new uncovered Borders as tuple.
        """
        if len(left) != len(right):
            raise ValueError(f"Borders must have same length")
        op_list = []
        op_list.extend(left.get_sab_list())
        op_list.extend(right.get_sab_list())
        op_list.sort(key = lambda x: x.coord)
        numerator = 0
        new_left = []
        new_right = []
        for sab in op_list:
            if sab.side == BorderSide.LEFT:
                numerator += 1
                if numerator == 1:
                    new_left.append(sab.coord)
            if sab.side == BorderSide.RIGHT:
                numerator -= 1
                if numerator == 0:
                    new_right.append(sab.coord)
            if numerator < 0:
                raise ValueError(f"Improper borders. Some alpha-cut ends before start!")
        return Border(new_left, side=BorderSide.LEFT), Border(new_right, side=BorderSide.RIGHT)


    @staticmethod
    def are_left_right(left: 'Border', right: 'Border') -> None:
        """
        Checks if two given left and right borders makes AlphaCut properly.
        :param left: Border Object with LEFT BorderSide flag.
        :param right: Border Object with RIGHT BorderSide flag.
        :return: None if everything is OK, otherwise raises ValueError of TypeError.
        """
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