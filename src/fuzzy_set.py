from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Union, cast
from decimal import Decimal
from abc import ABC, abstractmethod

from typing_extensions import override
from src.fs_types import Alpha

AlphaType = Union[float, Decimal, Fraction]
Numeric = Union[int, AlphaType]
BorderType = list[Numeric] | tuple[Numeric, ...] | Numeric


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
            
            # TODO [ KM - 1 ] Tutaj mozesz sprobowac zwiekszyc czytelnosc poprzez konstrukcje
            # for left_border, right_border in zip(narrow.left_borders, narrow.right_borders):
            #   index_to_check = next((index for index, value in enumerate(self.left_borders) if value >= left_border), -1)
            # Przy czym czytelnosc to pojecie wzgledne i moje rozwiazanie nie musi wydawac Ci sie bardziej czytelne,
            # bardziej wrzucam dla analizy kodu i innego podejscia

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

    def add_alpha_cut(self, alpha_cuts: AlphaCut | Iterable[AlphaCut]) -> "FuzzySet":
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

    def remove_alpha_cut(self, level: AlphaType) -> "FuzzySet":  # TODO [KM - 2] W takich miejscach piszemy Self
        if level in self._alpha_cuts.keys():
            self._alpha_cuts.pop(level)
            return self
        else:
            raise ValueError(f"There is no alpha-cut level {level} in fuzzy set.")

    def _sort_a_cuts(self):  # TODO [ KM - 3 ] Typ zwracany -> None
        self._alpha_cuts = dict(sorted(self._alpha_cuts.items(), reverse=True))

    def _check_alpha_levels_membership(self):  # TODO [ KM - 4 ] Typ zwracany -> None
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
                    ) -> "FuzzySet":
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
'''
@dataclass
class Tnorm(ABC):
    """
    Abstract class for T-norm calculations. Class is callable.
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm min
    """

    a: AlphaType
    b: AlphaType
    parameter: Numeric | None = None

    def __post_init__(self):
        self._types_validation()

    def _types_validation(self):
        if (not isinstance(self.a, float) and isinstance(self.b, float) or
                not isinstance(self.a, Decimal) and isinstance(self.b, Decimal)):
            raise TypeError("Parameters a and b have to be the same type.")
        if not isinstance(self.a, AlphaType) or not isinstance(self.b, AlphaType):
            raise TypeError("Parameters a and b be AlphaType type.")
        if not isinstance(self.parameter, Numeric | None):
            raise TypeError("Parameter parameter is not numeric.")

    @abstractmethod
    def __call__(self) -> AlphaType:
        pass

class Min(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm min
    """

    @override
    def __call__(self) -> AlphaType:

        return min(self.a, self.b)

class Product(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm product
    """

    @override
    def __call__(self) -> AlphaType:
        if isinstance(self.a, float):
            self.b = float(self.b)
            return cast(AlphaType, self.a * self.b)
        else: # isinstance(self.a, Decimal):
            self.b = Decimal(self.b)
            return cast(AlphaType, self.a * self.b)

class Lukasiewicz(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Lukasiewicz
    """

    @override
    def __call__(self) -> AlphaType:

        return max(0, self.a + self.b - 1)

class Drastic(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Drastic
    """

    @override
    def __call__(self) -> AlphaType:

        if self.a == 1:
            return self.b
        elif self.b == 1:
            return self.a
        else:
            return 0

class Nilpotent(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Nilpotent
    """

    @override
    def __call__(self) -> AlphaType:

        if self.a + self.b > 1:
            return min(self.a, self.b)
        else:
            return 0

class Hamacher(Tnorm):
    """
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Hamacher
    """

    @override
    def __call__(self) -> AlphaType:

        if self.a == self.b and self.a == 0:
            return 0
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
    def __call__(self) -> AlphaType:
        if self.parameter is None:
            raise AttributeError("Sklar's T-norm parameter can't be None.")

        if self.parameter == float('-inf'):
            return Min(self.a, self.b)()
        elif float('-inf') < self.parameter < 0:
            return (self.a ** self.parameter + self.b ** self.parameter - 1) ** (1 / self.parameter)
        elif self.parameter == 0:
            return Product(self.a * self.b)()
        elif 0 < self.parameter < float('inf'):
            return max(0, (self.a ** self.parameter + self.b ** self.parameter - 1) ** (1 / self.parameter))
        else: #  self.parameter == float('inf'):
            return Drastic(self.a, self.b)()


def main() -> None:
    aci = AlphaCut(0.1, (-10, ), (100, ))
    ac1 = AlphaCut(0.2, (1, 6), (3, 10))
    ac4 = AlphaCut(0.1, (0.0, 6.0), (5.0, 12.))
    ac5 = AlphaCut(0.2, (0.0, 6.0), (5.0, 12.))
    ac6 = AlphaCut(0.4, (1.0, 7.0), (5.0, 110.))
    fs = FuzzySet([ac4, ac5, ac6])


if __name__ == "__main__":
    main()
'''