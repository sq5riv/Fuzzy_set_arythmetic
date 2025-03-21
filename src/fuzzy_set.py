import pytest
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Union, cast
from decimal import Decimal
from abc import ABC, abstractmethod


from typing_extensions import override
from src.fs_types import Alpha, AlphaType, Numeric, BorderType

class AlphaCut:
    """
    Represents an α-cut of a fuzzy set.

    :param level: AlphaType-cut level.
    :param left_borders: Left borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    :param right_borders: Right borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    """

    def __init__(self, level: AlphaType | Alpha , left_borders: BorderType, right_borders: BorderType) -> None:
        self._level = level if isinstance(level, Alpha) else Alpha(level)
        self._same_type_check(left_borders, right_borders)
        self._left_borders = self._borders_prep(left_borders)
        self._right_borders = self._borders_prep(right_borders)
        self._borders_check()

    @staticmethod
    def _borders_prep(borders: BorderType) -> tuple[Numeric, ...]:
        if isinstance(borders, tuple) and all([isinstance(i, Numeric) for i in borders]):
            return borders
        if isinstance(borders, list) and all([isinstance(i, Numeric) for i in borders]):
            return tuple(borders)
        if isinstance(borders, Numeric):
            return tuple([borders])
        raise TypeError(f"Invalid borders type: {type(borders)}")

    @staticmethod
    def _same_type_check(left_borders: BorderType, right_borders: BorderType) -> None:
        if left_borders is None or right_borders is None:
            raise TypeError("Both left or right borders cannot be None")
        if isinstance(left_borders, tuple | list) and isinstance(right_borders, tuple | list):
            if len(left_borders) == 0 == len(right_borders):
                raise TypeError("Left or right borders can not be empty iterable")
            expected_type = type(left_borders[0])
            if not all([isinstance(border, expected_type) for border in left_borders]):
                raise TypeError(f"Not all borders are {expected_type}")
            if not all([isinstance(border, expected_type) for border in right_borders]):
                raise TypeError(f"Not all borders are {expected_type}")

        if type(left_borders) != type(right_borders):
            raise TypeError(f"Left_borders and right_borders "
                            f"must be the same type {type(left_borders), type(right_borders)}.")

    def _borders_check(self) -> None:
        if len(self.left_borders) != len(self.right_borders):
            raise ValueError("left and right borders must have same length.")
        if not all(left < right for left, right in zip(self.left_borders, self.right_borders)):
            raise ValueError("Alpha-cut have to has positive length.")
        if len(self.left_borders) != 1:
            if (not all([p < pp for p, pp in zip(self.left_borders, self.left_borders[1:])])
                    or not all([p < pp for p, pp in zip(self.right_borders, self.right_borders[1:])])):
                raise ValueError(f"Parts of alpha-cut have to be sorted.")
            if not all([left >= right for left, right in zip(self.left_borders[1:], self.right_borders[:-1])]):
                raise ValueError("Two parts of alpha-cut can't cover.")


    @property
    def level(self) -> AlphaType:
        return self._level.value

    @property
    def left_borders(self) -> tuple[Numeric, ...]:
        return self._left_borders

    @property
    def right_borders(self) -> tuple[Numeric, ...]:
        return self._right_borders

    def is_convex(self) -> bool:
        return len(self.left_borders) == 1 and len(self.right_borders) == 1

    def __contains__(self, narrow: Union['AlphaCut', Numeric]) -> bool:
        if isinstance(narrow, AlphaCut):
            if narrow.left_borders[0] < self.left_borders[0]:
                return False
            for left_border, right_border in zip(narrow.left_borders, narrow.right_borders):
                index_to_check = -1
                for index, value in enumerate(self.left_borders):
                    if value >= left_border:
                        index_to_check = index
                        break
                if right_border <= self.right_borders[index_to_check]:
                    continue
                else:
                    return False
            return True
        else:
            for left_border, right_border in zip(self.left_borders, self.right_borders):
                if left_border <= narrow <= right_border:
                    return True
            return False


    def is_wider(self, narrow: 'AlphaCut') -> bool:
        return narrow in self

    def __str__(self) -> str:
        return f'Alpha_cut({self.level}, {self.left_borders}, {self.right_borders})'

    def __repr__(self) -> str:
        return str(self)

class FuzzySet:
    """
    :param alpha_cuts: Iterable of alpha-cuts.
    """
    def __init__(self, alpha_cuts: Iterable[AlphaCut] | AlphaCut):
        self._alpha_cuts: dict[float|Decimal|Fraction, AlphaCut] = dict()
        for alpha_cut in alpha_cuts if not isinstance(alpha_cuts, AlphaCut) else (alpha_cuts,):
            if alpha_cut.level not in self._alpha_cuts.keys():
                self._alpha_cuts[alpha_cut.level] = alpha_cut
            else:
                raise ValueError(f"You have two Alpha-cuts with same level {alpha_cut.level}.")
        self._sort_a_cuts()
        self._check_alpha_levels_membership()

    def add_alpha_cut(self, alpha_cuts: AlphaCut | Iterable[AlphaCut]) -> 'FuzzySet':
        if isinstance(alpha_cuts, AlphaCut):
            alpha_cuts = (alpha_cuts,)
        for alpha_cut in alpha_cuts:
            if alpha_cut.level not in self._alpha_cuts.keys():
                self._alpha_cuts[alpha_cut.level] = alpha_cut
            else:
                raise ValueError(f"You have two Alpha-cuts with same level {alpha_cut.level}.")
        self._sort_a_cuts()
        self._check_alpha_levels_membership()
        return self

    def remove_alpha_cut(self, level: AlphaType) -> 'FuzzySet':
        if level in self._alpha_cuts.keys():
            self._alpha_cuts.pop(level)
            return self
        else:
            raise ValueError(f"There is no alpha-cut level {level} in fuzzy set.")

    def _sort_a_cuts(self) -> None:
        self._alpha_cuts = dict(sorted(self._alpha_cuts.items(), reverse=True))

    def _check_alpha_levels_membership(self) -> None:
        alpha_values = list(self._alpha_cuts.values())
        for i, j in zip(alpha_values[1:], alpha_values[:-1]):
            if j not in i:
                raise ValueError(f"Fuzzy set obstructed!")

    def check_membership_level(self, point: Numeric) -> AlphaType:
        for cut in self._alpha_cuts.values():
            if point in cut:
                return cut.level
        return 0

    @classmethod
    def from_points(cls, alpha_levels: tuple[AlphaType, ...],
                    points: Iterable[tuple[Numeric, Numeric]]
                    ) -> 'FuzzySet':
        """

        :param alpha_levels: tuple of given levels to generate AlphaCuts
        :param points: Iterable of points x and y to generate AlphaCuts and FuzzySet.
        y should be normalized to (0-1) range.
        :return: FuzzySet object
        """

        alpha_cuts_list = []
        check_run = True
        for level in alpha_levels:
            left_borders, right_borders = [], []
            last_coord = None
            in_cut = False
            for coord, value in points:
                if check_run and last_coord is not None:
                    if not last_coord < coord:
                        raise ValueError(f"Fuzzy set domain obstructed.")
                if value >= level and in_cut == False:
                    left_borders.append(coord)
                    in_cut = True
                if value < level and in_cut == True:
                    right_borders.append(last_coord)
                    in_cut = False
                last_coord = coord
            if len(left_borders) == len(right_borders) + 1:
                right_borders.append(last_coord)
            if len(left_borders) != 0:
                alpha_cuts_list.append(AlphaCut(level, left_borders, right_borders))
            check_run = False

        return cls(alpha_cuts_list)

@pytest.mark.skip(reason="Skipping tests for abstract class")
@dataclass
class Tnorm(ABC):
    """
    Abstract class for T-norm calculations. Class is callable.
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: T-norm parameter if needed.
    :return: returns T-norm value
    """

    a: Alpha
    b: Alpha
    parameter: float | None = None

    def __post_init__(self):
        self._types_validation()

    def _types_validation(self):
        if not (isinstance(self.a, Alpha) and isinstance(self.b, Alpha)):
            raise TypeError(f"T-norm calculation requires Alpha's.")
        self.a.is_types_the_same_type_and_return(self.b)

    def _set_zero_one_alpha(self) -> None:
        if isinstance(self.a.value, float):
            self.zero: Alpha = Alpha(0.0)
            self.one: Alpha = Alpha(1.0)
        elif isinstance(self.a.value, Decimal):
            self.zero: Alpha = Alpha(Decimal(0))
            self.one: Alpha = Alpha(Decimal(1))
        else:
            self.zero: Alpha = Alpha(Fraction(0))
            self.one: Alpha = Alpha(Fraction(1))

    @abstractmethod
    def __call__(self) -> Alpha:
        pass

class Min(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm min
    """

    @override
    def __call__(self) -> Alpha:

        return min(self.a, self.b)

class Max(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm max
    """

    @override
    def __call__(self) -> Alpha:

        return max(self.a, self.b)

class Product(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm product
    """

    @override
    def __call__(self) -> Alpha:
        return self.a * self.b


class Lukasiewicz(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Lukasiewicz
    """

    @override
    def __call__(self) -> Alpha:
        self._set_zero_one_alpha()
        v2 = self.a  + self.b - self.one
        v2.small_check = False
        return max(self.zero, v2)

class Drastic(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Drastic
    """

    @override
    def __call__(self) -> Alpha:
        self._set_zero_one_alpha()
        if self.a == self.one:
            return self.b
        elif self.b == self.one:
            return self.a
        else:
            return self.zero

class Nilpotent(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Nilpotent
    """

    @override
    def __call__(self) -> Alpha:
        self._set_zero_one_alpha()
        if self.a + self.b > self.one:
            return Min(self.a, self.b)()
        else:
            return self.zero

class Hamacher(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Hamacher
    """

    @override
    def __call__(self) -> Alpha:
        self._set_zero_one_alpha()
        if self.a == self.b and self.a == self.zero:
            return self.zero
        else:
            return (self.a * self.b) / (self.a + self.b - self.a * self.b)


class Sklar(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: parameter of Sklar's T-norm
    :return: returns T-norm Sklar
    """

    @override
    def __call__(self) -> Alpha:
        if isinstance(self.parameter, type(None)):
            raise AttributeError("Sklar's T-norm parameter can't be None.")
        if isinstance(self.a.value, Decimal):
            self.par_alpha = Alpha(Decimal(self.parameter), True)
        elif isinstance(self.a.value, Fraction):
            self.par_alpha = Alpha(Fraction(self.parameter), True)
        else:
            self.par_alpha = Alpha(self.parameter, True)
        self._set_zero_one_alpha()


        if self.parameter == float('-inf'):
            return Min(self.a, self.b)()
        elif float('-inf') < self.parameter < 0:
            ret_alpha = (self.a ** self.par_alpha + self.b ** self.par_alpha - self.one) ** (self.one / self.par_alpha)
            ret_alpha.small_check = False
            return ret_alpha
        elif self.parameter == 0:
            return Product(self.a, self.b)()
        elif 0 < self.parameter < float('inf'):
            mid_alpha = (self.a ** self.par_alpha + self.b ** self.par_alpha - self.one) ** (self.one / self.par_alpha)
            mid_alpha.small_check = False
            return Max(self.zero, mid_alpha)()
        else: #  self.parameter == float('inf'):
            return Drastic(self.a, self.b)()

