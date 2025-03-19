from decimal import Decimal
from fractions import Fraction
from typing import Union, Any, cast

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

    def is_types_the_same_type_and_return(self, other) -> type:
        rettype = type(other.value)
        if not isinstance(self.value, rettype):
            raise TypeError(f"Alphas has another types {type(self.value)} and {type(other.value)}. ")
        return rettype

    def __add__(self, other: "Alpha") -> "Alpha":
        try:
            cast_to = self.is_types_the_same_type_and_return(other)
            return Alpha(cast_to(self.value) + cast_to(other.value))
        except TypeError as e:
            raise TypeError(f"Cannot add {other} to {self}. {e}")


    def __sub__(self, other: "Alpha") -> "Alpha":
        try:
            cast_to = self.is_types_the_same_type_and_return(other)
            return Alpha(cast_to(self.value) - cast_to(other.value))
        except TypeError as e:
            raise TypeError(f"Cannot subtract {other} to {self}. {e}")


    def __mul__(self, other: "Alpha") -> "Alpha":
        try:
            cast_to = self.is_types_the_same_type_and_return(other)
            return Alpha(cast_to(self.value) * cast_to(other.value))
        except TypeError as e:
            raise TypeError(f"Cannot multiply {other} to {self}. {e}")


    def __eq__(self, other: Any) -> bool:
        """
        :param other: another Alpha membership object.
        :return: True if alpha levels are the same.
        """
        if not isinstance(other, Alpha):
            return False
        try:
            self.is_types_the_same_type_and_return(other)
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
        
        # TODO [ KM - 1 ] Wytarczy return self.borders == other.borders
        if self.borders == other.borders:
            return True
        else:
            return False

    @staticmethod
    def are_left_right(left: 'Border', right: 'Border') -> bool:
        # TODO [ KM - 2 ] Kiedy masz raise a na koniec return mozesz pisac bez elif czyli
        #  if warunek1
        #     raise ..
        #  if warunek2
        #     raise ..
        #  ...
        #  return ...
        # I tez mamy ten "konflikt" czy w przypadku funkcji ktora zwraca bool
        # nie robic tak, ze jesli cos nie gra to zwracamy False a jak ok to True
        # czyli zamiast raise stosowac return False, ale moze byc tak ze rzucanie
        # roznego rodzaju wyjatkow moze potem byc obslugiwane na rozne sposoby, wtedy
        # pomysalbym o zrobieniu tej metody ze zwraca None i wywolujemy ja na zasadzie
        # ze jesli nie ma wyjatku to idziemy dalej
        if type(left.dtrial) != type(right.dtrial):
            raise TypeError(f"Borders must have the same data type")
        elif len(left) != len(right):
            raise ValueError(f"Borders must have the same length")
        elif not all(l <= r for l, r in zip(left.borders, right.borders)):
            raise ValueError(f"Alpha_cut length cant be negative")
        # TODO [ KM - 3 ] Tutaj nie pamietam, czy juz nie bylo podobnej dyskusji, ze nie potrzeba
        #  [] w all, ale type checker moze sie "czepiac". Sprawdz to prosze.
        elif not all([left >= right for left, right in zip(left.borders[1:], right.borders[:-1])]):
            raise ValueError("Two parts of alpha-cut can't cover.")
        elif left.covered or right.covered:
            raise ValueError(f"Borders must be not covered to be borders of fuzzy-set. Use uncover class-method")
        else:
            return True

    @classmethod
    def uncover(cls, left: 'Border', right: 'Border') -> tuple['Border', 'Border']:
        sleft = sorted(left.borders)
        sright = sorted(right.borders)
        l_max = len(sleft)
        r_max = len(sright)
        if sright[0] < sleft[0]:
            raise ValueError(f"First right border can't be lower than first left border")
        if l_max != r_max:
            raise ValueError(f"Borders must have same length")
        counter = 0
        new_left = []
        new_right = []
        l_pointer = 0
        r_pointer = 0
        while r_pointer < r_max:
            if l_pointer < l_max and sleft[l_pointer] < sright[r_pointer]:
                if counter == 0: new_left.append(sleft[l_pointer])
                l_pointer += 1
                counter += 1
            elif l_pointer < l_max and sleft[l_pointer] > sright[r_pointer]:
                counter -= 1
                if counter == 0: new_right.append(sright[r_pointer])
                r_pointer += 1
            else:
                counter -= 1
                if counter == 0: new_right.append(sright[r_pointer])
                r_pointer += 1
        return Border(new_left), Border(new_right)

    def __add__(self, other: 'Border') -> "Border":
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

    def __sub__(self, other: 'Border') -> "Border":  # TODO [ KM - 4 ] W takich miejscach Self
        cast_to = type(self.dtrial)
        if not isinstance(other.dtrial, cast_to):
            raise TypeError(f"To add borders must have the same data type")
        def convert(value1, value2) -> Numeric:
            if cast_to is Decimal:
                return Decimal(value1) - Decimal(value2)
            elif cast_to is Fraction:
                return Fraction(value1) - Fraction(value2)
            elif cast_to is float:
                return float(value1) - float(value2)
            else:
                return int(value1) - int(value2)

        result: list[Numeric] =cast(list[Numeric],
                    [convert(sborder, oborder)
                    for sborder in self.borders
                    for oborder in other.borders])
        return Border(result, True)

