import pytest
from typing import cast
from decimal import Decimal
from fractions import Fraction

from fuzzy_set_arythmetic.alpha import Alpha


@pytest.mark.parametrize("a", [0.,
                               0.5,
                               1.,
                               Decimal(0.1),
                               Decimal(0.5),
                               Decimal(1.0),
                               Fraction(1, 2)])
def test_alpha_proper_type(a):
    assert Alpha(a)


@pytest.mark.parametrize("a", [0,
                               1 + 5j,
                               'a'])
def test_alpha_improper_type(a):
    with pytest.raises(TypeError, match="Alpha value must be a float, Decimal or Fraction,"):
        Alpha(a)


@pytest.mark.parametrize("a", [1.00001,
                               -.00001,
                               42.0,
                               Fraction(25, 16)])
def test_alpha_improper_value(a):
    with pytest.raises(ValueError, match="Alpha-cut level must be between 0 and 1."):
        Alpha(a)


@pytest.mark.parametrize("a1, a2, ty", [(0.5, 0.5, float),
                                        (Decimal(0.5), Decimal(0.5), Decimal),
                                        (Fraction(1, 2), Fraction(1, 2), Fraction)
                                        ])
def test_alpha_is_types_the_same_type_proper(a1, a2, ty):
    alpha1 = Alpha(a1)
    alpha2 = Alpha(a2)
    assert alpha1.check_and_get_type(alpha2) is ty


@pytest.mark.parametrize("a1, a2", [(0.5, Decimal(0.5)),
                                    (Decimal(0.5), Fraction(1, 2)),
                                    (Fraction(1, 2), 0.5)
                                    ])
def test_alpha_is_types_the_same_type_improper(a1, a2):
    with pytest.raises(TypeError, match=f"Alphas has another types"):
        alpha1 = Alpha(a1)
        alpha2 = Alpha(a2)
        alpha1.check_and_get_type(alpha2)


@pytest.mark.parametrize("a1, a2, res", [(0.5, 0.5, 1.0),
                                         (Decimal(0.5), Decimal(0.5), Decimal(1.0)),
                                         (Fraction(1, 2), Fraction(1, 2), Fraction(1, 1)),
                                         ])
def test_alpha__add__proper(a1, a2, res):
    alpha1 = Alpha(a1)
    alpha2 = Alpha(a2)
    r_alpha = Alpha(res)
    assert alpha1 + alpha2 == r_alpha


@pytest.mark.parametrize("a1, a2, res", [(0.5, Decimal(0.5), 1.0),
                                         (Decimal(0.5), Fraction(1, 2), 1.0),
                                         (Fraction(1, 2), 0.5, 1.0)
                                         ])
def test_alpha__add__improper(a1, a2, res):
    with pytest.raises(TypeError, match=f"Cannot add"):
        alpha1 = Alpha(a1)
        alpha2 = Alpha(a2)
        r_alpha = Alpha(res)
        assert alpha1 + alpha2 == r_alpha


@pytest.mark.parametrize("a1, a2, res", [(0.5, 0.5, 0.0),
                                         (Decimal(0.5), Decimal(0.5), Decimal(0.0)),
                                         (Fraction(1, 2), Fraction(1, 2), Fraction(0, 1)),
                                         ])
def test_alpha__sub__proper(a1, a2, res):
    alpha1 = Alpha(a1)
    alpha2 = Alpha(a2)
    r_alpha = Alpha(res)
    assert alpha1 - alpha2 == r_alpha


@pytest.mark.parametrize("a1, a2, res", [(0.5, Decimal(0.5), 0.0),
                                         (Decimal(0.5), Fraction(1, 2), 0.0),
                                         (Fraction(1, 2), 0.5, 0.0)
                                         ])
def test_alpha__sub__improper(a1, a2, res):
    with pytest.raises(TypeError, match=f"Cannot subtract"):
        alpha1 = Alpha(a1)
        alpha2 = Alpha(a2)
        r_alpha = Alpha(res)
        assert alpha1 - alpha2 == r_alpha


@pytest.mark.parametrize("a1, a2, res", [(0.5, 0.5, 0.25),
                                         (Decimal(0.5), Decimal(0.5), Decimal(0.25)),
                                         (Fraction(1, 2), Fraction(1, 2), Fraction(1, 4)),
                                         ])
def test_alpha__mul__(a1, a2, res):
    alpha1 = Alpha(a1)
    alpha2 = Alpha(a2)
    r_alpha = Alpha(res)
    assert alpha1 * alpha2 == r_alpha


@pytest.mark.parametrize("a1, a2, res", [(0.5, Decimal(0.5), 1.0),
                                         (Decimal(0.5), Fraction(1, 2), 1.0),
                                         (Fraction(1, 2), 0.5, 1.0)
                                         ])
def test_alpha__mul__improper(a1, a2, res):
    with pytest.raises(TypeError, match=f"Cannot multiply"):
        alpha1 = Alpha(a1)
        alpha2 = Alpha(a2)
        r_alpha = Alpha(res)
        assert alpha1 * alpha2 == r_alpha


@pytest.mark.parametrize("a1, a2", [(0.5, 0.5),
                                    (Decimal(0.5), Decimal(0.5)),
                                    (Fraction(1, 2), Fraction(1, 2)),
                                    ])
def test_alpha__eq__proper(a1, a2):
    alpha1 = Alpha(a1)
    alpha2 = Alpha(a2)
    assert alpha1 == alpha2


@pytest.mark.parametrize("a1, a2", [(0.5, 0.5),
                                    (Decimal(0.5), Decimal(0.5)),
                                    (Fraction(1, 2), Fraction(1, 2)),
                                    ])
def test_alpha__eq__improper_type(a1, a2):
    assert (Alpha(a1) == a2) is False


@pytest.mark.parametrize("a1, a2", [(0.5, 0.4),
                                    (Decimal(0.5), Decimal(0.4)),
                                    (Fraction(1, 2), Fraction(1, 3)),
                                    ])
def test_alpha_not__eq__(a1, a2):
    alpha1 = Alpha(a1)
    alpha2 = Alpha(a2)
    assert alpha1 != alpha2


@pytest.mark.parametrize("a1, a2", [(0.5, Decimal(0.5)),
                                    (Decimal(0.5), Fraction(1, 2)),
                                    (Fraction(1, 2), 0.5)
                                    ])
def test_alpha__eq__improper(a1, a2):
    with pytest.raises(TypeError, match=f"Cannot compare"):
        alpha1 = Alpha(a1)
        alpha2 = Alpha(a2)
        assert alpha1 == alpha2


def test_alpha__repr__():
    alpha = Alpha(0.5)
    assert repr(alpha) == "Alpha(0.5)"


@pytest.mark.parametrize("a, b", [(Alpha(0.5), Alpha(0.6)), ])
def test_alpha__lt__(a, b):
    assert a < b


@pytest.mark.parametrize("a, b", [(Alpha(0.6), Alpha(0.5)), ])
def test_alpha__gt__(a, b):
    assert a > b


@pytest.mark.parametrize("a", [Alpha(0.0), Alpha(Decimal(0.5))])
def test_alpha__truediv__improper(a: Alpha):
    with pytest.raises((ValueError, TypeError), match=f"Cannot divide*|"
                                                      f"Cannot divide by 0"):
        a0 = Alpha(1.0)
        zonk = a0 / a


def test_alpha__pow__improper():
    with pytest.raises(TypeError, match=f"Cannot raise*"):
        zonk = Alpha(0.5) ** Alpha(Decimal(0.5))


def test_check_and_do_given_operation_improper():
    with pytest.raises(TypeError, match=f"You can't make operation on Alpha and*"):
        a0 = Alpha(0.5)
        a1 = cast(Alpha, 0.5)
        a0._check_and_do_given_operation(a1, lambda x, y: x + y, 'Ala ma kota')
