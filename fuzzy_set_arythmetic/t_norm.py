from dataclasses import dataclass
from fractions import Fraction
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import override

from fuzzy_set_arythmetic.alpha import Alpha


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
        self.a.check_and_get_type(self.b)

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
    T-norm calculation for min t-norm.
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
    T-norm calculation for max t-norm.
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
    T-norm calculation for product t-norm.
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
    T-norm calculation for lukasiewicz t-norm.
    :param a: AlphaType level of AlphaCut
    :param b: AlphaType level of AlphaCut
    :param parameter: Not used
    :return: returns T-norm Lukasiewicz
    """

    @override
    def __call__(self) -> Alpha:
        self._set_zero_one_alpha()
        v2 = self.a + self.b - self.one
        v2.small_check = False
        return max(self.zero, v2)


class Drastic(Tnorm):
    """
    T-norm calculation for drastic t-norm.
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
    T-norm calculation for nilpotent t-norm.
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
    T-norm calculation for Hamacher's t-norm.
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
    T-norm calculation for Sklar's t-norm.
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
        else:  #  self.parameter == float('inf'):
            return Drastic(self.a, self.b)()
