import pytest
from typing import cast

from src.fuzzy_set import AlphaCut, Numeric, Alcs
from src.fs_types import Border, BorderSide, SaB, Alpha



def test_alpha_cut() -> None:
    assert AlphaCut(0.1, 0.0, 1.0)

@pytest.mark.parametrize("a", [Alpha(0.),Alpha(0.5),Alpha(1.)])
def test_get_alpha_level(a: float) -> None:
    ac = AlphaCut(a, 0.0, 1.0)
    assert ac.level == a

@pytest.mark.parametrize("a", [0.,0.5,1.])
def test_alpha_cut_correct_level(a: float) -> None:
    assert AlphaCut(a, 0.0, 1.0)

@pytest.mark.parametrize("a", [-0.1, 1.1])
def test_alpha_cut_incorrect_level(a: float) -> None:
    with pytest.raises(ValueError, match="Alpha-cut level must be between 0 and 1."):
         AlphaCut(a, 0.0, 1.0)

@pytest.mark.parametrize("left_borders, right_borders", [(1, 2),
                                                         (2, 3),
                                                         ((1, 5), (3, 7)),
                                                         ([1, 5],[3, 7])
                                                         ])
def test_border_prep_corect(left_borders, right_borders) -> None:
    ac = AlphaCut(0.1, left_borders, right_borders)
    if isinstance(left_borders, Numeric):
        assert ac.left_borders == Border(left_borders)
    if isinstance(right_borders, Numeric):
        assert ac.right_borders == Border(right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [(1, (2, 3)),
                                                         ((1, 3), 2),
                                                         (('a', 1), (1, 2)),
                                                         ((1.2, 1), (2, 3)),
                                                         ('a','b'),
                                                         (('a','b'),('c','d')),
                                                         ((1, 2), (1, 'c')),
                                                         (None, 1),
                                                         ([],[])
                                                         ])
def test_border_prep_incorect(left_borders: float, right_borders: float ) -> None:
    with pytest.raises((ValueError, TypeError), match=r"(Borders must have the same length|"
                                                      r"Border must be of type Numeric,*|"
                                                      r"All elements of border must be the same type|"
                                                      r"border must be of type BorderType, not*|"
                                                      r"border cannot be empty|"
                                                      r"Left or right borders can not be empty iterable)"):
        AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((1, 2),(2, 3)),
                                                         ((1, 5), (3, 7))])
def test_alpha_cut_correct_borders(left_borders: float, right_borders: float ) -> None:
    assert AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((1, 3), (2, 4, 5)),
                                                         ((1, 2), (3, 4)),
                                                         ((1, 3), (6, 10))])
def test_alpha_cut_incorrect_borders(left_borders: float, right_borders: float ) -> None:
    with pytest.raises(ValueError, match=r"(Borders must have the same length|"
                                         r"Two parts of alpha-cut can't cover.)"):
        AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((2, 3), (1, 4)),
                                                         ((5, 2), (6, 3))])
def test_alpha_cut_incorrect_cut_length(left_borders: float, right_borders: float ) -> None:
    with pytest.raises(ValueError, match="(Alpha_cut length cant be negative|"
                                         "Two parts of alpha-cut can't cover.)"):
        AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((1,),(2,)), ((1,), (5,))])
def test_alpha_cut_convex(left_borders: float, right_borders: float ) -> None:
    ac = AlphaCut(0.1, left_borders, right_borders)
    assert ac.is_convex() is True

@pytest.mark.parametrize("left_borders, right_borders", [((1, 2),(2, 3)), ((1, 5), (3, 7))])
def test_alpha_cut_not_convex(left_borders: float, right_borders: float ) -> None:
    ac = AlphaCut(0.1, left_borders, right_borders)
    assert ac.is_convex() is False

def test_alpha_cut_repr():
    ac = AlphaCut(0.1, 0, 1)
    assert ac.__repr__() == f'Alpha_cut(Alpha(0.1), Border((0,)), Border((1,)))'

@pytest.mark.parametrize("left_borders, right_borders", [((1, 6), (3, 10)),
                                                         ((1, 6), (3, 20)),
                                                         ((0, 5), (4, 11))])
def test_alpha_cut_is_wider_and__contains__(left_borders: float, right_borders: float ) -> None:
    ac0 = AlphaCut(0.1, (0, 5),(4, 100))
    ac1 = AlphaCut(0.1, left_borders, right_borders)
    assert ac0.is_wider(ac1) is True

@pytest.mark.parametrize("left_borders, right_borders", [((1, 6), (3, 120)),
                                                         ((-1, 5), (4, 11)),
                                                         ((-10, 5), (4, 11)),
                                                         ((39,), (50,))])
def test_alpha_cut_not_is_wider_and_not__contains__(left_borders: float, right_borders: float ) -> None:
    ac0 = AlphaCut(0.1, (0,),(20,))
    ac1 = AlphaCut(0.1, left_borders, right_borders)
    assert ac0.is_wider(ac1) is False

@pytest.mark.parametrize('tested_number', [0, 1, 19, 20])
def test_alpha_cut_in_number(tested_number: int) -> None:
    ac0 = AlphaCut(0.1, (0,), (20,))
    assert tested_number in ac0

@pytest.mark.parametrize('tested_number', [-1, 21])
def test_alpha_cut_not_in_number(tested_number: int) -> None:
    ac0 = AlphaCut(0.1, (0, 25), (20, 50))
    assert tested_number not in ac0

def test_alpha_cut_set_sides() -> None:
    ac0 = AlphaCut(0.1, Border((0, 25)), Border((20, 50)))
    assert ac0.left_borders.side == BorderSide.LEFT
    assert ac0.right_borders.side == BorderSide.RIGHT

def test_alpha_cut_from_bordersides():
    sab0 = SaB(BorderSide.LEFT, 1.0)
    sab1 = SaB(BorderSide.RIGHT, 2.0)
    assert (AlphaCut.from_bordersides(0.1, [sab0, sab1]) ==
            AlphaCut(0.1, 1.0, 2.0))

def test_alpha_cut_from_bordersides_improper() -> None:
    with pytest.raises(ValueError, match=r"Border list must contain only SaB objects."):
        sab0 = SaB(BorderSide.LEFT, 1.0)
        sab1 = SaB(BorderSide.RIGHT, 2.0)
        AlphaCut.from_bordersides(0.1, [sab0, sab1, cast(SaB, 1)])

@pytest.mark.parametrize("a", [AlphaCut(0.2, 2, 3),
                               AlphaCut(0.1, 3, 3),
                               AlphaCut(0.1, 2, 4),
                               'XD'])
def test_alpha_cut__eq__false(a: AlphaCut) -> None:
    a0 = AlphaCut(0.1, 2, 3)
    assert a != a0

def test_alpha_cut_get_alcs() -> None:
    ac = AlphaCut(0.2,1,3)
    alcs = ac.get_alcs()
    assert alcs[0] == Alcs(0.2, 1.0, BorderSide.LEFT)
    assert alcs[1] == Alcs(0.2, 3.0, BorderSide.RIGHT)
    assert alcs[2] == Alcs(0.2, 1.0606060606060606, BorderSide.INSIDE)
