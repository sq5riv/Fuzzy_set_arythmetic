from collections import defaultdict
from typing import Iterable, Self
from src.fs_types import Alcs, Alpha, AlphaType, Border, BorderSide, BorderType, Numeric, SaB
from src.t_norm import Tnorm

class AlphaCut:
    """
    Represents n alpha-cut of a fuzzy set.
    :param level: AlphaType-cut level.
    :param left_borders: Left borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    :param right_borders: Right borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    """

    def __init__(self, level: AlphaType | Alpha , left_borders: Border | BorderType, right_borders: Border | BorderType) -> None:
        self._level = level if isinstance(level, Alpha) else Alpha(level)
        self._left_borders: Border = left_borders if isinstance(left_borders, Border) else Border(left_borders, side= BorderSide.LEFT)
        self._right_borders: Border = right_borders if isinstance(right_borders, Border) else Border(right_borders, side= BorderSide.RIGHT)
        self._borders_check()

    def _borders_check(self) -> None:
        """
        Checks if given borders makes proper alpha cut. If not raise an error.
        :return:
        """
        if self._left_borders.side is None:
            self._left_borders.side = BorderSide.LEFT
        if self._right_borders.side is None:
            self._right_borders.side = BorderSide.RIGHT
        Border.are_left_right(self._left_borders, self._right_borders)

    @property
    def level(self) -> Alpha:
        return self._level

    @property
    def left_borders(self) -> Border:
        return self._left_borders

    @property
    def right_borders(self) -> Border:
        return self._right_borders

    def is_convex(self) -> bool:
        return len(self.left_borders) == 1 and len(self.right_borders) == 1

    def __contains__(self, narrow: Numeric | 'AlphaCut') -> bool:
        """
        Check if Alpha cut or point is in another AlphaCut.
        :param narrow: alpha cut or point to check.
        :return: True if Alpha cut or point is in another AlphaCut.
        """
        if isinstance(narrow, AlphaCut):
            if narrow.left_borders.borders[0] < self.left_borders.borders[0]:
                return False
            for left_border, right_border in zip(narrow.left_borders.borders, narrow.right_borders.borders):
                index_to_check = -1
                for index, value in enumerate(self.left_borders.borders):
                    if value >= left_border:
                        index_to_check = index
                        break
                if right_border <= self.right_borders.borders[index_to_check]:
                    continue
                else:
                    return False
            return True
        else:
            for left_border, right_border in zip(self.left_borders.borders, self.right_borders.borders):
                if left_border <= narrow <= right_border:
                    return True
            return False

    def is_wider(self, narrow: 'AlphaCut') -> bool:
        return narrow in self

    def __str__(self) -> str:
        return f'Alpha_cut({self.level}, {self.left_borders}, {self.right_borders})'

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AlphaCut):
            return False
        if self.level != other.level:
            return False
        if self.left_borders != other.left_borders:
            return False
        if self.right_borders != other.right_borders:
            return False
        return True

    def invert(self) -> 'AlphaCut':
        cast_to = type(self.left_borders.dtrial)
        new_left = self.right_borders * Border(cast_to(-1.0))
        new_right = self.left_borders * Border(cast_to(-1.0))
        new_right.side = BorderSide.RIGHT
        new_left.side = BorderSide.LEFT
        return AlphaCut(self.level.value, *Border.uncover(new_left, new_right))

    @classmethod
    def from_bordersides(cls, level: AlphaType | Alpha, said_and_border: list[SaB]) -> 'AlphaCut':
        """
        Build AlphaCut object from said and border coord tuple.
        :param level: Alphacut level between 0 and 1.
        :param said_and_border: list of points describes. Alpha-cut.
        :return:
        """
        left = []
        right = []
        if not all(isinstance(sab, SaB) for sab in said_and_border):
            raise ValueError(f'Border list must contain only SaB objects.')
        [left.append(sab.Coord) if sab.Side == BorderSide.LEFT else right.append(sab.Coord) for sab in said_and_border]
        return AlphaCut(level, left, right)

    def get_alcs(self) -> list[Alcs]:
        retlist = []
        for left, right in zip(self.left_borders.borders, self.right_borders.borders):
            retlist.append(Alcs(float(self.level.value), float(left), BorderSide.LEFT))
            retlist.append(Alcs(float(self.level.value), float(right), BorderSide.RIGHT))
            point = float(left)
            eps = (float(right) - point) / 33
            while (point := point + eps) < right:
                retlist.append(Alcs(float(self.level.value), float(point), BorderSide.INSIDE))

        return retlist


# TODO [ KM - 6 ] Przy takiej ilosci kodu i rozdzielnosci odpowiedzialnosc klas AlphaCut i FuzzySet
#  zdecydowalbym sie na rozdzielnie tych klas na dwa osobne moduly

class FuzzySet:
    """
    :param alpha_cuts: Iterable of alpha-cuts.
    """
    def __init__(self, alpha_cuts: Iterable[AlphaCut] | AlphaCut):
        self._alpha_cuts: dict[Alpha, AlphaCut] = dict()
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
            if not self.check_membership_level(alpha_cut.level):
                self._alpha_cuts[alpha_cut.level] = alpha_cut
            else:
                raise ValueError(f"You have two Alpha-cuts with same level {alpha_cut.level}.")
        self._sort_a_cuts()
        self._check_alpha_levels_membership()
        return self

    @property
    def alpha_cuts(self) -> list[AlphaCut]:
        return list(self._alpha_cuts.values())

    def remove_alpha_cut(self, level: AlphaType | Alpha) -> 'FuzzySet':
        lvl = level if isinstance(level, Alpha) else Alpha(level)
        if lvl in self._alpha_cuts.keys():
            self._alpha_cuts.pop(lvl)
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FuzzySet):
            return False
        if all(acs == aco for acs, aco in zip(self.alpha_cuts, other.alpha_cuts)):
            return True
        else:
            return False

    def check_membership_level(self, point: Alpha | AlphaType) -> bool:
        """
        Returns True if the given alpha level value is in fuzzy set.
        :param point: Tested alpha level value
        :return: True if the given alpha level value is in fuzzy set.
        """
        point = point if isinstance(point, Alpha) else Alpha(point)
        return point in self._alpha_cuts.keys()


    @classmethod
    def from_points(cls, alpha_levels: tuple[AlphaType, ...],
                    points: Iterable[tuple[Numeric, Numeric]]
                    ) -> Self:
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

    def add_with_tnorm(self, other: 'FuzzySet', tnorm: type['Tnorm'] ) -> Self:
        mid_alpha: defaultdict[Alpha, list[SaB]] = defaultdict(list)
        for sac in self.alpha_cuts:
            for oac in other.alpha_cuts:
                new_alpha = tnorm(sac.level, oac.level)
                new_alpha = new_alpha()
                new_left = sac.left_borders + oac.left_borders
                new_right = sac.right_borders + oac.right_borders
                new_left.side = BorderSide.LEFT
                new_right.side = BorderSide.RIGHT
                mid_alpha[new_alpha].extend(new_left.get_sab_list())
                mid_alpha[new_alpha].extend(new_right.get_sab_list())
        alpha_list = []
        for k, v in mid_alpha.items():
            alpha_list.append(AlphaCut.from_bordersides(k, v))
        return FuzzySet(alpha_cuts=alpha_list)

    def invert(self) -> Self:
        new_alpha_cuts = []
        [new_alpha_cuts.append(v.invert()) for k, v in self._alpha_cuts.items()]
        return FuzzySet(alpha_cuts=new_alpha_cuts)

    def sub_with_tnorm(self, other: 'FuzzySet', tnorm: type['Tnorm'] ) -> Self:
        return self.add_with_tnorm(other.invert(), tnorm)

    def get_points_to_plot(self) -> list[Alcs]:
        retlist = []
        # TODO [ KM - 4 ] Tutaj poszedlbym w klasyczna petle for bez zbednego list comprehension
        [retlist.extend(a.get_alcs()) for a in self.alpha_cuts]
        return retlist
