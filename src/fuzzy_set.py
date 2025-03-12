from typing import Iterable, Union
from decimal import Decimal


Numeric = int | float | Decimal
Border = list[Numeric] | tuple[Numeric, ...] | Numeric

class AlphaCut:
    """
    Represents an α-cut of a fuzzy set.

    :param level: Alpha-cut level.
    :param left_borders: Left borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    :param right_borders: Right borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    """

    def __init__(self, level: float | Decimal, left_borders: Border, right_borders: Border) -> None:
        self._level = level
        self._same_type_check(left_borders, right_borders)
        self._left_borders = self._borders_prep(left_borders)
        self._right_borders = self._borders_prep(right_borders)
        self._level_check()
        self._borders_check()

    @staticmethod
    def _borders_prep(borders: Border) -> tuple[Numeric, ...]:
        if isinstance(borders, tuple) and all([isinstance(i, Numeric) for i in borders]):
            return borders
        if isinstance(borders, list) and all([isinstance(i, Numeric) for i in borders]):
            return tuple(borders)
        if isinstance(borders, Numeric):
            return tuple([borders])
        raise TypeError(f"Invalid borders type: {type(borders)}")

    @staticmethod
    def _same_type_check(left_borders: Border, right_borders: Border) -> None:
        if left_borders is None or right_borders is None:
            raise ValueError("Both left and right borders cannot be None")
        if isinstance(left_borders, tuple | list) and isinstance(right_borders, tuple | list):
            expected_type = type(left_borders[0])
            if not all([isinstance(border, expected_type) for border in left_borders]):
                raise TypeError(f"Not all borders are {expected_type}")
            if not all([isinstance(border, expected_type) for border in right_borders]):
                raise TypeError(f"Not all borders are {expected_type}")

        if type(left_borders) != type(right_borders):
            raise TypeError(f"Left_borders and right_borders "
                            f"must be the same type {type(left_borders), type(right_borders)}.")

    def _level_check(self) -> None:
        if 0 > self._level or self._level > 1:
            raise ValueError("Alpha-cut level must be between 0 and 1.")

    def _borders_check(self) -> None:
        if len(self.left_borders) != len(self.right_borders):
            raise ValueError("left and right borders must have same length.")
        if not all([left < right for left, right in zip(self.left_borders, self.right_borders)]):
            raise ValueError("Alpha-cut have to has positive length.")
        if len(self.left_borders) != 1:
            if (not all([p < pp for p, pp in zip(self.left_borders, self.left_borders[1:])])
                    or not all([p < pp for p, pp in zip(self.right_borders, self.right_borders[1:])])):
                raise ValueError(f"Parts of alpha-cut have to be sorted.")
            if not all([left >= right for left, right in zip(self.left_borders[1:], self.right_borders[:-1])]):
                raise ValueError("Two parts of alpha-cut can't cover.")


    @property
    def level(self) -> float | Decimal:
        return self._level

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
        self._alpha_cuts: dict[float|Decimal, AlphaCut] = dict()
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

    def remove_alpha_cut(self, level: float | Decimal) -> 'FuzzySet':
        if level in self._alpha_cuts.keys():
            self._alpha_cuts.pop(level)
            return self
        else:
            raise ValueError(f"There is no alpha-cut level {level} in fuzzy set.")

    def _sort_a_cuts(self):
        self._alpha_cuts = dict(sorted(self._alpha_cuts.items(), reverse=True))

    def _check_alpha_levels_membership(self):

        for i, j in zip(list(self._alpha_cuts.values())[1:], list(self._alpha_cuts.values())[:-1]):
            if j not in i:
                pass
                #raise ValueError(f"Fuzzy set obstructed!")

    def check_membership_level(self, point: Numeric) -> float | Decimal:
        for cut in self._alpha_cuts.values():
            if point in cut:
                return cut.level
        return 0

def main() -> None:
    aci = AlphaCut(0.1, (-10, ), (100, ))
    ac1 = AlphaCut(0.2, (1, 6), (3, 10))
    ac4 = AlphaCut(0.1, (0.0, 6.0), (5.0, 12.))
    ac5 = AlphaCut(0.2, (0.0, 6.0), (5.0, 12.))
    ac6 = AlphaCut(0.4, (1.0, 7.0), (5.0, 11.))
    fs = FuzzySet([ac4, ac5, ac6])


if __name__ == "__main__":
    main()