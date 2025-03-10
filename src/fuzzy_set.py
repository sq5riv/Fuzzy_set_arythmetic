from collections import defaultdict
from typing import Iterable, DefaultDict
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

        # TODO [ KM 1 ] Kiedy masz return to nie musisz pisac if ... elif ... elif ... tylko same if
        if isinstance(borders, tuple) and all([isinstance(i, Numeric) for i in borders]):
            return borders
        if isinstance(borders, list) and all([isinstance(i, Numeric) for i in borders]):
            return tuple(borders)
        if isinstance(borders, Numeric):
            return tuple([borders])
        raise TypeError(f"Invalid borders type: {type(borders)}")

    @staticmethod
    def _same_type_check(left_borders: Border, right_borders: Border) -> None:
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
            print(self.left_borders[1:], self.right_borders[:-1])
            if not all([left <= right for left, right in zip(self.left_borders[1:], self.right_borders[:-1])]):
                raise ValueError("Two parts of alpha-cut can't cover.")
            if (not all([p < pp for p, pp in zip(self.left_borders, self.left_borders[1:])])
                    or not all([p < pp for p, pp in zip(self.right_borders, self.right_borders[1:])])):
                raise ValueError(f"Parts of alpha-cut have to be sorted.")

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
        return True if len(self.left_borders) == 1 and len(self.right_borders) == 1 else False

    def __str__(self) -> str:
        return f'Alpha_cut({self.level}, {self.left_borders}, {self.right_borders})'

    def __repr__(self) -> str:
        return str(self)

class FuzzySet:
    """
    :param alpha_cuts: Iterable of alpha-cuts.
    """
    def __init__(self, alpha_cuts: Iterable[AlphaCut] | AlphaCut):
        self._alpha_cuts: DefaultDict[float|Decimal, AlphaCut] = defaultdict()
        for alpha_cut in alpha_cuts if not isinstance(alpha_cuts, AlphaCut) else (alpha_cuts,):
            if alpha_cut.level not in self._alpha_cuts.keys():
                self._alpha_cuts[alpha_cut.level] = alpha_cut
            else:
                raise ValueError(f"You have two Alpha-cuts with same level {alpha_cut.level}.")

    def add_alpha_cut(self, alpha_cuts: AlphaCut | Iterable[AlphaCut]) -> 'FuzzySet':
        for alpha_cut in (alpha_cuts,) if not isinstance(alpha_cuts, Iterable) else alpha_cuts:
            print(self._alpha_cuts.keys(), alpha_cut)
            if alpha_cut.level not in self._alpha_cuts.keys():
                self._alpha_cuts[alpha_cut.level] = alpha_cut
            else:
                raise ValueError(f"You have two Alpha-cuts with same level {alpha_cut.level}.")
        return self

    def remove_alpha_cut(self, level: float | Decimal) -> 'FuzzySet':
        if level in self._alpha_cuts.keys():
            self._alpha_cuts.pop(level)
            return self
        else:
            raise ValueError(f"There is no alpha-cut level {level} in fuzzy set.")

# TODO [ KM 2 ] Brak dokumentacji w README, nie wiadomo co projekt robi, jak go uruchomic, jakie ma pokrycie
#  kodu testami, jakie wyniki statycznej analizy kodu, jaka wersja python, scenariusze uzycia, jesli repo
#  w PyPI to link to repo

def main() -> None:
    ac0 = AlphaCut(0.01, 0.0, 1.0)
    ac1 = AlphaCut(0.1, 0.0, 1.0)
    ac2 = AlphaCut(0.1, 0.0, 1.0)
    ac3 = AlphaCut(0.3, 0.0, 1.0)
    fs = FuzzySet([ac1, ac3])
    fs.add_alpha_cut(ac0)
    fs.add_alpha_cut(ac1)
    print(fs)

if __name__ == "__main__":
    main()