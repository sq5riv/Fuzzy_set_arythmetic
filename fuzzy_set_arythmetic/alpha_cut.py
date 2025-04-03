from fuzzy_set_arythmetic.alpha import Alpha
from fuzzy_set_arythmetic.border import Border
from fuzzy_set_arythmetic.types import Alcs, AlphaType, BorderSide, BorderType, Numeric, SaB


class AlphaCut:
    """
    Represents n alpha-cut of a fuzzy set.
    :param level: AlphaType-cut level.
    :param left_borders: Left borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    :param right_borders: Right borders of the alpha-cut. If more than one value is present, the fuzzy set is not convex.
    """

    def __init__(self, level: AlphaType | Alpha,
                 left_borders: Border | BorderType,
                 right_borders: Border | BorderType) -> None:
        self._level = level if isinstance(level, Alpha) else Alpha(level)
        self._left_borders: Border = left_borders if isinstance(left_borders, Border) else Border(left_borders,
                                                                                                  side=BorderSide.LEFT)
        self._right_borders: Border = right_borders if isinstance(right_borders, Border) else Border(right_borders,
                                                                                                     side=BorderSide.RIGHT)
        self._borders_check()

    def __str__(self) -> str:
        return f'Alpha_cut({self.level}, {self.left_borders}, {self.right_borders})'

    def __repr__(self) -> str:
        return str(self)

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
        """
        :return: Returns membership level.
        """
        return self._level

    @property
    def left_borders(self) -> Border:
        """
        :return: Border object describes left borders of AlphaCut.
        """
        return self._left_borders

    @property
    def right_borders(self) -> Border:
        """
        :return: Border object describes right borders of AlphaCut.
        """
        return self._right_borders

    def is_convex(self) -> bool:
        """
        Check if AlphaCut is convex. Convex Fuzzy set got all convex AlphaCut.
        :return: True if AlphaCut is convex, False if not.
        """
        return len(self.left_borders) == 1 and len(self.right_borders) == 1

    def is_wider(self, narrow: 'AlphaCut') -> bool:
        """
        checks if given AlphaCut contains in this AlphaCut.
        :param narrow: Another AlphaCut object.
        :return: True if AlphaCut is wider, False if not.
        """
        return narrow in self

    def invert(self) -> 'AlphaCut':
        """
        Returns inverted AlphaCut.
        :return: AlphaCut inverted.
        """
        cast_to = type(self.left_borders.dtrial)
        new_left = self.right_borders * Border(cast_to(-1.0))
        new_right = self.left_borders * Border(cast_to(-1.0))
        new_right.side = BorderSide.RIGHT
        new_left.side = BorderSide.LEFT
        return AlphaCut(self.level.value, *Border.uncover(new_left, new_right))

    def get_alcs(self) -> list[Alcs]:
        """
        :return: Returns AlphaCut ad list of points to plot.
        Left, Right ends and some inside points to describe AlphaCut.
        """
        retlist = []
        for left, right in zip(self.left_borders.borders, self.right_borders.borders):
            retlist.append(Alcs(float(self.level.value), float(left), BorderSide.LEFT))
            retlist.append(Alcs(float(self.level.value), float(right), BorderSide.RIGHT))
            point = float(left)
            eps = (float(right) - point) / 33
            while (point := point + eps) < right:
                retlist.append(Alcs(float(self.level.value), float(point), BorderSide.INSIDE))

        return retlist

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
        [left.append(sab.coord) if sab.side == BorderSide.LEFT else right.append(sab.coord) for sab in said_and_border]
        left, right = Border.uncover(Border(left, True, BorderSide.LEFT), Border(right, True, BorderSide.RIGHT))
        return AlphaCut(level, left, right)
