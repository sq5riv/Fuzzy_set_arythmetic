from src.fuzzy_set import AlphaCut, Numeric
import pytest


def test_alpha_cut() -> None:
    assert AlphaCut(0.1, 0.0, 1.0)

@pytest.mark.parametrize("a", [0,0.5,1])
def test_get_alpha_level(a: float) -> None:
    ac = AlphaCut(a, 0.0, 1.0)
    assert ac.level == a

@pytest.mark.parametrize("a", [0,0.5,1])
def test_alpha_cut_correct_level(a: float) -> None:
    assert AlphaCut(a, 0.0, 1.0)

@pytest.mark.parametrize("a", [-0.1, 1.1])
def test_alpha_cut_incorrect_level(a: float) -> None:
    with pytest.raises(ValueError, match="Alpha-cut level must be between 0 and 1."):
         AlphaCut(a, 0.0, 1.0)

@pytest.mark.parametrize("left_borders, right_borders", [(1, 2),(2, 3),
                                                         ((1, 3), (5, 7)),
                                                         ([1, 3],[5, 7])
                                                         ])
def test_border_prep_corect(left_borders, right_borders) -> None:
    ac = AlphaCut(0.1, left_borders, right_borders)
    if isinstance(left_borders, Numeric):
        assert ac.left_borders == tuple([left_borders])
    if isinstance(right_borders, Numeric):
        assert ac.right_borders == tuple([right_borders])

@pytest.mark.parametrize("left_borders, right_borders", [(1, (2, 3)), ((1, 3), 2),
                                                         (('a', 1), (1, 2)),
                                                         ((1.2, 1), (2, 3)),
                                                         ('a','b'),
                                                         (('a','b'),('c','d')),
                                                         ((1, 2), (1, 'c'))
                                                         ])
def test_border_prep_incorect(left_borders: float, right_borders: float ) -> None:
    with pytest.raises(TypeError, match=r"(Invalid borders type:*|Not all borders are*|Left_borders and right_borders must be the same type*)"):
        AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((1, 2),(2, 3)), ((1, 3), (5, 7))])
def test_alpha_cut_correct_borders(left_borders: float, right_borders: float ) -> None:
    assert AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((1, 3), (2, 4, 5)), ((1, 3), (2, 4))])
def test_alpha_cut_incorrect_borders(left_borders: float, right_borders: float ) -> None:
    with pytest.raises(ValueError, match=r"(left and right borders must have same length.|Two parts of alpha-cut can't cover.)"):
        AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((2, 3), (1, 4)), ((5, 2), (6, 3))])
def test_alpha_cut_incorrect_cut_length(left_borders: float, right_borders: float ) -> None:
    with pytest.raises(ValueError, match="(Parts of alpha-cut have to be sorted.|Alpha-cut have to has positive length.)"):
        AlphaCut(0.1, left_borders, right_borders)

@pytest.mark.parametrize("left_borders, right_borders", [((1,),(2,)), ((1,), (5,))])
def test_alpha_cut_convex(left_borders: float, right_borders: float ) -> None:
    ac = AlphaCut(0.1, left_borders, right_borders)
    assert ac.is_convex() is True

@pytest.mark.parametrize("left_borders, right_borders", [((1, 2),(2, 3)), ((1, 3), (5, 7))])
def test_alpha_cut_not_convex(left_borders: float, right_borders: float ) -> None:
    ac = AlphaCut(0.1, left_borders, right_borders)
    assert ac.is_convex() is False

def test_repr():
    ac = AlphaCut(0.1, 0, 1)
    assert ac.__repr__() == f'Alpha_cut(0.1, (0,), (1,))'