import pytest
from decimal import Decimal
from fractions import Fraction

from src.border import Border
from src.types import BorderSide


@pytest.mark.parametrize("b", [0.5,
                               5,
                               Decimal(0.5),
                               Fraction(1, 2),
                               [1, 2, 3],
                               (1, 2, 3),
                               (1, 1)])
def test_border_init(b):
    assert Border(b)


@pytest.mark.parametrize("b", ['a',
                               1 + 2j,
                               {'a': 1}])
def test_border_init_improper(b):
    with pytest.raises(TypeError, match=f"border must be of type BorderType, not"):
        Border(b)


@pytest.mark.parametrize("b", [('1', '2'),
                               (1, 1.1)])
def test_border_check(b):
    with pytest.raises(TypeError, match=f"Border must be of type Numeric, not|"
                                        f"All elements of border must be the same type"):
        Border(b)


def test_border_str():
    assert str(Border(1)) == "Border((1,))"


@pytest.mark.parametrize("b, expect", [((1, 1), True),
                                       ((2, 1), True),
                                       ((1, 2), False)])
def test_border_covered(b, expect):
    assert Border(b).covered is expect


def test_border_dtrial():
    assert Border([1, 2, 3]).dtrial is 1


def test_border_borders():
    assert Border([1, 2, 3]).borders == (1, 2, 3)


def test_border_empty_border():
    with pytest.raises(ValueError, match=f"border cannot be empty"):
        Border([])


@pytest.mark.parametrize("b1, b2", [(Border([1, 2, 3]), Border([1, 2, 4])),
                                    (Border([1, 2, 3]), 'Duck')])
def test_border__eq__false(b1, b2):
    assert (b1 == b2) is False


@pytest.mark.parametrize("left, right", [(Border(1.), Border(2.))])
def test_border_are_left_and_right_proper(left, right):
    assert Border.are_left_right(left, right) is None


@pytest.mark.parametrize("left, right", [(Border(1.), Border(Decimal(2.))),
                                         (Border((1., 2.)), Border(1.)),
                                         (Border((2., 15.)), Border((1., 30.))),
                                         (Border(-2., True), Border(-1., True)),
                                         (Border((-2., 2.)), Border((3., 5.)))])
def test_border_are_left_and_right_improper(left, right):
    with pytest.raises((ValueError, TypeError), match=f"Borders must have the same length|"
                                                      f"Borders must be not covered to be borders of fuzzy-set.|"
                                                      f"Alpha_cut length cant be negative|"
                                                      f"Two parts of alpha-cut can't cover.|"
                                                      f"Borders must have the same data type"):
        Border.are_left_right(left, right)


@pytest.mark.parametrize("left, right, new_left, new_right", [(Border(1., side=BorderSide.LEFT),
                                                               Border(2., side=BorderSide.RIGHT),
                                                               Border(1., side=BorderSide.LEFT),
                                                               Border(2., side=BorderSide.RIGHT)),
                                                              (Border((2., 1.), side=BorderSide.LEFT),
                                                               Border((1.5, 2.5), side=BorderSide.RIGHT),
                                                               Border((1., 2.), side=BorderSide.LEFT),
                                                               Border((1.5, 2.5), side=BorderSide.RIGHT))])
def test_border_uncover(left, right, new_left, new_right):
    left, right = Border.uncover(left, right)
    assert left.covered is False
    assert right.covered is False
    assert left == new_left
    assert right == new_right


@pytest.mark.parametrize("left, right", [(Border(1., side=BorderSide.LEFT), Border(-1., side=BorderSide.RIGHT)),
                                         (Border(2., side=BorderSide.LEFT), Border((3., 4.), side=BorderSide.RIGHT))])
def test_border_uncover_improper(left, right):
    with pytest.raises(ValueError, match=f"Improper borders. Some alpha-cut ends before start!|"
                                         f"Borders must have same length"):
        Border.uncover(left, right)


@pytest.mark.parametrize("left, right, result", [(Border(1.), Border(-1.), Border(0.)),
                                                 (Border(2.), Border(3.), Border(5.)),
                                                 (Border(Decimal(2.)), Border(Decimal(3.)), Border(Decimal(5.))),
                                                 (Border(Fraction(1, 2)), Border(Fraction(1, 3)),
                                                  Border(Fraction(5, 6))),
                                                 (Border(2), Border(3), Border(5)),
                                                 (Border([1, 2, 3, 4, 5]), Border([9, 8, 7, 6, 5]),
                                                  Border([10, 9, 8, 7, 6, 11,
                                                          10, 9, 8, 7, 12, 11,
                                                          10, 9, 8, 13, 12, 11,
                                                          10, 9, 14, 13, 12, 11,
                                                          10]))])
def test_border__add__proper(left, right, result):
    assert Border.__add__(left, right) == result


@pytest.mark.parametrize("left, right", [(Border(1.), Border(1)),
                                         (Border(Decimal(2)), Border(1))])
def test_border__add__improper(left, right):
    with pytest.raises(TypeError, match=f"To add borders must have the same data type"):
        Border.__add__(left, right)


@pytest.mark.parametrize("left, right, result", [(Border(1.), Border(-1.), Border(2.)),
                                                 (Border(2.), Border(3.), Border(-1.)),
                                                 (Border(Decimal(2.)), Border(Decimal(3.)), Border(Decimal(-1.))),
                                                 (Border(Fraction(1, 2)), Border(Fraction(1, 3)),
                                                  Border(Fraction(1, 6))),
                                                 (Border(2), Border(3), Border(-1)),
                                                 (Border([1, 2, 3, 4, 5]), Border([9, 8, 7, 6, 5]),
                                                  Border([-8, -7, -6, -5, -4,
                                                          -7, -6, -5, -4, -3,
                                                          -6, -5, -4, -3, -2,
                                                          -5, -4, -3, -2, -1,
                                                          -4, -3, -2, -1, 0]))])
def test_border__sub__proper(left, right, result):
    assert Border.__sub__(left, right) == result


@pytest.mark.parametrize("left, right", [(Border(1.), Border(1)),
                                         (Border(Decimal(2)), Border(1))])
def test_border__sub__improper(left, right):
    with pytest.raises(TypeError, match=f"To subtract borders must have the same data type"):
        Border.__sub__(left, right)


@pytest.mark.parametrize("left, right, result", [(Border(1.), Border(-1.), Border(-1.)),
                                                 (Border(2.), Border(3.), Border(6.)),
                                                 (Border(Decimal(2.)), Border(Decimal(3.)), Border(Decimal(6.))),
                                                 (Border(Fraction(1, 2)), Border(Fraction(1, 3)),
                                                  Border(Fraction(1, 6))),
                                                 (Border(2), Border(3), Border(6)),
                                                 (Border([1, 2, 3, 4, 5]), Border([-1]), Border([-1, -2, -3, -4, -5]))])
def test_border__mul__proper(left, right, result):
    assert Border.__mul__(left, right) == result


@pytest.mark.parametrize("left, right", [(Border(1.), Border(1)),
                                         (Border(Decimal(2)), Border(1)),
                                         (Border((1, 2)), Border((1, 2)))
                                         ])
def test_border__mul__improper(left, right):
    with pytest.raises((TypeError, ValueError),
                       match=f"To multiplied borders must have the same data type|"
                             f"You can't multiply by Border with more than one border"):
        Border.__mul__(left, right)


def test_border_get_sab_list_improper():
    with pytest.raises(TypeError, match="Cannot get sab list from None side value"):
        b0 = Border(Decimal(0))
        zonk = b0.get_sab_list()
