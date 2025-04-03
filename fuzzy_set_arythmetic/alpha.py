from typing import Any, Callable, Self

from fuzzy_set_arythmetic.types import AlphaType


class Alpha:
    """
    :param value: membership level between 0 and 1.
    :param small_check: Default False, if True requirement of being between 0 and 1 is off, used for t-norm calculations.
    """

    def __init__(self, value: AlphaType, small_check: bool = False):
        self._value: AlphaType = value
        self._small_check: bool = small_check
        self._type_check()

    def __repr__(self) -> str:
        return f"Alpha({self.value})"

    def __str__(self) -> str:
        return self.__repr__()

    def __add__(self, other: "Alpha") -> Self:
        return self._check_and_do_given_operation(other,
                                                  lambda a, b: a + b,
                                                 f"Cannot add {other} to {self}.")

    def __sub__(self, other: "Alpha") -> Self:
        return self._check_and_do_given_operation(other,
                                                  lambda a, b: a - b,
                                                 f"Cannot subtract {other} to {self}.")

    def __mul__(self, other: "Alpha") -> Self:
        return self._check_and_do_given_operation(other,
                                                  lambda a, b: a * b,
                                                 f"Cannot multiply {other} to {self}.")

    def __truediv__(self, other: "Alpha") -> Self:
        if other.value == 0:
            raise ValueError("Cannot divide by 0")
        return self._check_and_do_given_operation(other,
                                                  lambda a, b: a / b,
                                                 f"Cannot divide {other} to {self}.")

    def __pow__(self, other: "Alpha") -> Self:
        return self._check_and_do_given_operation(other,
                                                  lambda a, b: a ** b,
                                                 f"Cannot raise {other} to {self}.")

    def __eq__(self, other: Any) -> bool:
        """
        :param other: another Alpha membership object.
        :return: True if alpha levels are the same.
        """
        if not isinstance(other, Alpha):
            return False
        try:
            self.check_and_get_type(other)
        except TypeError as e:
            raise TypeError(f"Cannot compare {other} to {self}. {e}")
        return self.value == other.value

    def __lt__(self, other: "Alpha") -> bool:
        return self.value < other.value

    def __gt__(self, other: "Alpha") -> bool:
        return self.value > other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def _type_check(self):
        if not isinstance(self.value, AlphaType):
            raise TypeError(f"Alpha value must be a float, Decimal or Fraction, not {type(self.value)}")
        if not self.small_check and not (0 <= self.value <= 1):
            raise ValueError(f"Alpha-cut level must be between 0 and 1. Given value: {self.value}")

    def _check_and_do_given_operation(self, other: "Alpha", operation: Callable, error_message: str) -> Self:
        if not isinstance(other, Alpha):
            raise TypeError(f"You can't make operation on Alpha and {type(other)} class")
        oper1 = self.value
        oper2 = other.value
        if not isinstance(oper1, type(oper2)):
            raise TypeError(f"Alphas has another types {type(self.value)} and {type(other.value)}. {error_message}")
        else:
            return Alpha(operation(oper1, oper2), True)

    @property
    def value(self) -> AlphaType:
        """
        :return: membership level between 0 and 1.
        """
        return self._value

    @property
    def small_check(self) -> bool:
        """
        :return: small check state. If True membership level between 0 and 1 is not check.
        """
        return self._small_check


    @small_check.setter
    def small_check(self, small_check: bool):
        """
        :param small_check: small check state. If true membership level between 0 and 1 is not check.
        If you set False, membership level have to be between 0 and 1, another ValueError will be raised.
        """
        self._small_check = small_check
        self._type_check()


    def check_and_get_type(self, other) -> type:
        """
        :param other: another Alpha membership object.
        :return: type of Alpha level. It's one of AlphaType.
        """
        rettype = type(other.value)
        if not isinstance(self.value, rettype):
            raise TypeError(f"Alphas has another types {type(self.value)} and {type(other.value)}. ")
        return rettype



