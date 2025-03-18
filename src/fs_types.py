from decimal import Decimal
from fractions import Fraction
from typing import Type, Union, get_args, Any

AlphaType = Union[float, Decimal, Fraction]
Numeric = Union[int, AlphaType]
BorderType = list[Numeric] | tuple[Numeric, ...] | Numeric

class Alpha:
    """
    :param value: membership level between 0 and 1.
    """
    def __init__(self, value: AlphaType):
        self._value: AlphaType = value
        self._type_check()

    def _type_check(self):
        if not isinstance(self.value, AlphaType):
            raise TypeError(f"Alpha value must be a float, Decimal or Fraction, not {type(self.value)}")
        if  not 1 >= self.value >= 0:
            raise ValueError("Alpha-cut level must be between 0 and 1.")

    @property
    def value(self) -> AlphaType:
        return self._value

    # TODO [ KM - 6 ] Mozesz pomysle tutaj nad zmiana nazwy metody poniewaz jak piszesz is_.. to sugerujesz
    #  ze metoda zwraca bool
    def _is_types_the_same_type(self, other) -> type:
        rettype = type(other.value)
        if not isinstance(self.value, rettype):
            raise TypeError(f"Alphas has another types {type(self.value)} and {type(other.value)}. ")
        return rettype

    def __add__(self, other: "Alpha") -> "Alpha":
        try:
            cast = self._is_types_the_same_type(other)
            # TODO [ KM - 7] Tutaj sie wszystko ok dodalo? Funkcja cast zwraca type i zastanawia mnie
            #  jaki bedzie efekt dodawania dwoch type? Moze lepiej najpierw sprawdzic zgodnosc typow a 
            #  potem po prostu dodac obiekty, kiedy zgodnosc typow zachodzi. Sprawdz to prosze jeszcze.
            return Alpha(cast(self.value) + cast(other.value))
        except TypeError as e:
            raise TypeError(f"Cannot add {other} to {self}. {e}")


    def __sub__(self, other: "Alpha") -> "Alpha":
        try:
            cast = self._is_types_the_same_type(other)
            return Alpha(cast(self.value) - cast(other.value))
        except TypeError as e:
            raise TypeError(f"Cannot subtract {other} to {self}. {e}")


    def __mul__(self, other: "Alpha") -> "Alpha":
        try:
            cast = self._is_types_the_same_type(other)
            return Alpha(cast(self.value) * cast(other.value))
        except TypeError as e:
            raise TypeError(f"Cannot multiply {other} to {self}. {e}")


    def __eq__(self, other: Any) -> bool:
        """
        :param other: another Alpha membership object.
        :return: True if alpha levels are the same.
        """

        # TODO [ KM - 4 ] W __eq__ w obliczu problemu zwraca False lub NotImplemented nie robimy raise
        if not isinstance(other, Alpha):
            raise NotImplementedError(f"Cannot compare {self} to {other}")
        try:
            self._is_types_the_same_type(other)
        except TypeError as e:
            raise TypeError(f"Cannot compare {other} to {self}. {e}")
        return self.value == other.value

    def __repr__(self) -> str:
        return f"Alpha({self.value})"

    def __str__(self) -> str:
        return self.__repr__()

class Border:
    def __init__(self, border: BorderType, covered: bool = False) -> None:
        self._set_border(border)
        self._covered = covered
        self._dtrial = self._border[0]
        self._check()

    def _set_border(self, border: BorderType) -> None:
        if isinstance(border, Numeric):
            self._border = (border,)
        elif isinstance(border, tuple | list):
            self._border = tuple(border)
        else:
            raise TypeError(f"border must be of type BorderType, not {type(border)}")


    def _check(self) -> None:
        print(self._dtrial, type(self._dtrial))
        if not isinstance(self._dtrial, Numeric):
            raise TypeError(f"Border must be of type Numeric, not {type(self._dtrial)}")
        if not all(isinstance(elem, type(self._dtrial)) for elem in self._border):
            raise TypeError(f"All elements of border must be the same type")
        
        # TODO [ KM - 5 ] Mozna pomyslec nad:
        # if any(last <= nxt for last, nxt in zip(self._border[:-1], self._border[1:])):
        #    self._covered = True
        for last, nxt in zip(self._border[:-1], self._border[1:]):
            if last <= nxt:
                self._covered = True
                break

    def __repr__(self) -> str:
        return f"Border({self._border})"

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self):
        return len(self._border)

    @property
    def covered(self) -> bool:
        """
        :return: covered flag.
        """
        return self._covered

    @property
    def dtrial(self) -> BorderType:
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

    @staticmethod
    def are_left_right(left: 'Border', right: 'Border') -> bool:
        # TODO [KM - 8] Ta uwaga jest bardziej dla upewnienia sie ze to co podajesz jako argumenty zip
        #  czyli left.borders oraz right.borders ma te same wymiary, zeby zip wszystko polaczyl w pary,
        #  chyba ze nie potrzebujesz polaczenia kazdy z kazdym. Jesli to nie zostalo wczesniej sprawdzone
        #  mozesz tutaj zwrocic na to uwage.
        if type(left.dtrial) != type(right.dtrial):
            raise TypeError(f"Borders must have the same data type")
        elif len(left) != len(right):
            raise ValueError(f"Borders must have the same length")
        elif not all(l <= r for l, r in zip(left.borders, right.borders)):
            raise ValueError(f"Alpha_cut length cant be negative")
        elif not all([left >= right for left, right in zip(left.borders[1:], right.borders[:-1])]):
            raise ValueError("Two parts of alpha-cut can't cover.")
        elif left.covered or right.covered:
            raise ValueError(f"Borders must be not covered to be borders of fuzzy-set. Use uncover class-method")
        else:
            return True
"""
    @classmethod
    def uncover(cls, left: 'Border', right: 'Border') -> tuple('Border', 'Border'):
        steps = len(left.borders) + len(right.borders) - 2
        liter = iter(left.borders)
        riter = iter(right.borders)
        lv = next(liter)
        rv = next(riter)
        count = 0
        new_left = []
        new_right = []
        for i in range(steps)
"""