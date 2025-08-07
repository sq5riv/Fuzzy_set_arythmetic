from collections import defaultdict
from typing import Iterable, Self

from fuzzy_set_arythmetic.alpha import Alpha
from fuzzy_set_arythmetic.types import Alcs, AlphaType, BorderSide, Numeric, SaB
from fuzzy_set_arythmetic.t_norm import Tnorm
from fuzzy_set_arythmetic.alpha_cut import AlphaCut


class FuzzySet:
    """
    Class describes Fuzzyset as tuple of AlphaCuts.
    Has add and subtract methods.
    Fuzzy set can be non-convex.
    :param alpha_cuts: Iterable of alpha-cuts or AlphaCut.
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FuzzySet):
            return False
        if all(acs == aco for acs, aco in zip(self.alpha_cuts, other.alpha_cuts)):
            return True
        else:
            return False

    def _sort_a_cuts(self) -> None:
        self._alpha_cuts = dict(sorted(self._alpha_cuts.items(), reverse=True))

    def _check_alpha_levels_membership(self) -> None:
        alpha_values = list(self._alpha_cuts.values())
        for i, j in zip(alpha_values[1:], alpha_values[:-1]):
            if j not in i:
                raise ValueError(f"Fuzzy set obstructed!")

    @property
    def alpha_cuts(self) -> list[AlphaCut]:
        """
        Returns list of alpha-cuts contained by FuzzySet object.
        :return: List of AlphaCut.
        """
        return list(self._alpha_cuts.values())

    def add_alpha_cut(self, alpha_cuts: AlphaCut | Iterable[AlphaCut]) -> Self:
        """
        Add alpha-cuts to FuzzySet object.
        :param alpha_cuts: AlphaCut or Iterable of AlphaCuts.
        :return: FuzzySet instance itself.
        """
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

    def remove_alpha_cut(self, level: AlphaType | Alpha) -> Self:
        """
        Removes indicated alpha-cut from FuzzySet object.
        :param level: Alpha level points to remove alpha cut from.
        :return: FuzzySet instance itself.
        """
        lvl = level if isinstance(level, Alpha) else Alpha(level)
        if lvl in self._alpha_cuts.keys():
            self._alpha_cuts.pop(lvl)
            return self
        else:
            raise ValueError(f"There is no alpha-cut level {level} in fuzzy set.")

    def check_membership_level(self, point: Alpha | AlphaType) -> bool:
        """
        Returns True if the given alpha level value is in fuzzy set.
        :param point: Tested alpha level value
        :return: True if the given alpha level value is in fuzzy set.
        """
        point = point if isinstance(point, Alpha) else Alpha(point)
        return point in self._alpha_cuts.keys()

    def add_with_tnorm(self, other: 'FuzzySet', tnorm: type['Tnorm']) -> Self:
        """
        Ads two FuzzySet objects into a new FuzzySet object with Tnorm.
        :param other: fuzzy set object to add.
        :param tnorm: Tnorm Class object.
        :return: FuzzySet added object.
        """
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
        """
        Inverts fuzzy set by 0 element of domain.
        :return: FuzzySet object.
        """
        new_alpha_cuts = []
        for k, v in self._alpha_cuts.items():
            new_alpha_cuts.append(v.invert())
        return FuzzySet(alpha_cuts=new_alpha_cuts)

    def sub_with_tnorm(self, other: 'FuzzySet', tnorm: type['Tnorm']) -> Self:
        """
        Subtract other FuzzySet object from this FuzzySet object with Tnorm.
        :param other: FuzzySet object to subtract.
        :param tnorm: Tnorm class object.
        :return: FuzzySet subtracted object.
        """
        return self.add_with_tnorm(other.invert(), tnorm)

    def get_points_to_plot(self) -> list[Alcs]:
        """
        Returns list of points represent fuzzy-set to plot.
        :return: List of points in specific format.
        """
        retlist = []
        for a in self.alpha_cuts:
            retlist.extend(a.get_alcs())
        return retlist

    @classmethod
    def from_points(cls, alpha_levels: tuple[AlphaType, ...],
                    points: Iterable[tuple[Numeric, AlphaType]]
                    ) -> Self:
        """
        Builds FuzzySet from given points.
        :param alpha_levels: tuple of given levels to generate AlphaCuts
        :param points: Iterable of points x and y to generate AlphaCuts and FuzzySet.
        x is part of fuzzy-set domain.
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
