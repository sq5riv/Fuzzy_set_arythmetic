import pytest
from decimal import Decimal
from fractions import Fraction

from src.alpha import Alpha
from src.t_norm import Min, Max, Product, Lukasiewicz, Drastic, Nilpotent, \
    Hamacher, Sklar


@pytest.mark.parametrize("a1, a2", [(Alpha(0.5), Alpha(0.5)), ])
def test_t_norm_proper(a1, a2) -> None:
    Min(a1, a2)


@pytest.mark.parametrize("a1, a2", [(Alpha(0.5), 0.5),
                                    (Alpha(0.5), Alpha(Decimal(0.5))), ])
def test_t_norm_improper(a1, a2) -> None:
    with pytest.raises(TypeError, match=f"T-norm calculation requires Alpha's.|"
                                        f"Alphas has another types"):
        Min(a1, a2)


@pytest.mark.parametrize("a1, a2, res", [(Alpha(0.5), Alpha(0.6), Alpha(0.5)), ])
def test_t_norm_min(a1, a2, res) -> None:
    assert Min(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, res", [(Alpha(0.5), Alpha(0.6), Alpha(0.6)), ])
def test_t_norm_max(a1, a2, res) -> None:
    assert Max(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, res", [(Alpha(0.5), Alpha(0.5), Alpha(0.25)),
                                         (Alpha(Decimal(0.5)), Alpha(Decimal(0.5)), Alpha(Decimal(0.25))),
                                         (Alpha(Fraction(1, 2)), Alpha(Fraction(1, 2)), Alpha(Fraction(1, 4))), ])
def test_t_norm_product(a1, a2, res) -> None:
    assert Product(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, res", [(Alpha(0.5), Alpha(0.75), Alpha(0.25)),
                                         (Alpha(Decimal(0.5)), Alpha(Decimal(0.75)), Alpha(Decimal(0.25))),
                                         (Alpha(Fraction(1, 2)), Alpha(Fraction(3, 4)), Alpha(Fraction(1, 4))), ])
def test_t_norm_lukasiewicz(a1, a2, res) -> None:
    assert Lukasiewicz(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, res", [(Alpha(1.0), Alpha(0.75), Alpha(0.75)),
                                         (Alpha(0.75), Alpha(1.0), Alpha(0.75)),
                                         (Alpha(0.9), Alpha(0.75), Alpha(0.0)),
                                         (Alpha(Decimal(1.0)), Alpha(Decimal(0.75)), Alpha(Decimal(0.75))),
                                         (Alpha(Decimal(0.9)), Alpha(Decimal(0.75)), Alpha(Decimal(0.0))),
                                         (Alpha(Fraction(1)), Alpha(Fraction(1, 4)), Alpha(Fraction(1, 4))),
                                         (Alpha(Fraction(9, 10)), Alpha(Fraction(1, 4)), Alpha(Fraction(0))), ])
def test_t_norm_drastic(a1, a2, res) -> None:
    assert Drastic(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, res", [(Alpha(1.0), Alpha(0.75), Alpha(0.75)),
                                         (Alpha(0.2), Alpha(0.75), Alpha(0.0)),
                                         (Alpha(Decimal(1.0)), Alpha(Decimal(0.75)), Alpha(Decimal(0.75))),
                                         (Alpha(Decimal(0.2)), Alpha(Decimal(0.75)), Alpha(Decimal(0.0))),
                                         (Alpha(Fraction(1)), Alpha(Fraction(1, 4)), Alpha(Fraction(1, 4))),
                                         (Alpha(Fraction(5, 10)), Alpha(Fraction(1, 4)), Alpha(Fraction(0))), ])
def test_t_norm_nilpotent(a1, a2, res) -> None:
    assert Nilpotent(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, res", [(Alpha(0.0), Alpha(0.0), Alpha(0.0)),
                                         (Alpha(0.5), Alpha(0.5), Alpha(.3333333333333333)),
                                         (Alpha(Decimal(1.0)), Alpha(Decimal(0.75)), Alpha(Decimal(0.75))),
                                         (Alpha(Decimal(1)), Alpha(Decimal(0.5)), Alpha(Decimal(0.5))),
                                         (Alpha(Fraction(1)), Alpha(Fraction(1, 4)), Alpha(Fraction(1, 4))),
                                         (Alpha(Fraction(5, 10)), Alpha(Fraction(1, 2)), Alpha(Fraction(1, 3))), ])
def test_t_norm_hamacher(a1, a2, res) -> None:
    assert Hamacher(a1, a2)() == res


@pytest.mark.parametrize("a1, a2, p, res", [(Alpha(0.0), Alpha(0.0), 0.0, Alpha(0.0)),
                                            (Alpha(Decimal(0.0)), Alpha(Decimal(0.0)), 0.0, Alpha(Decimal(0.0))),
                                            (Alpha(Fraction(0.0)), Alpha(Fraction(0.0)), 0.0, Alpha(Fraction(0.0))),
                                            (Alpha(1.0), Alpha(0.0), float('-inf'), Alpha(0.0)),
                                            (Alpha(1.0), Alpha(1.0), -2.0, Alpha(1.0)),
                                            (Alpha(1.0), Alpha(1.0), 2.0, Alpha(1.0)),
                                            (Alpha(1.0), Alpha(0.0), float('+inf'), Alpha(0.0)),
                                            ])
def test_t_norm_sklar(a1, a2, p, res) -> None:
    assert Sklar(a1, a2, p)() == res


def test_t_norm_sklar_improper() -> None:
    with pytest.raises(AttributeError, match="Sklar's T-norm parameter can't be None."):
        Sklar(Alpha(0.0), Alpha(0.0))()
