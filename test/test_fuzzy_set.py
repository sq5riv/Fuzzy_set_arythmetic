import pytest
from decimal import Decimal
from typing import Iterable, cast

from src.types import BorderSide
from src.fuzzy_set import AlphaCut, FuzzySet, Numeric, Alcs
from src.t_norm import Min

ac0 = AlphaCut(0.01, 0.0, 1.0)
ac1 = AlphaCut(0.1, 0.0, 1.0)
ac2 = AlphaCut(0.1, 0.0, 1.0)
ac3 = AlphaCut(0.3, 0.0, 1.0)
ac4 = AlphaCut(0.1, (0.0, 6.0), (5.0, 10.))
ac5 = AlphaCut(0.2, (1.0, 7.0), (4.0, 9.))
ac6 = AlphaCut(0.4, (2.0, 8.0), (3.0, 8.5))
ac7 = AlphaCut(0.5, (2.0, 8.0), (3.0, 15.))


@pytest.mark.parametrize("a", [ac1, [ac2], (ac3,)])
def test_fuzzy_set(a: Iterable[AlphaCut]) -> None:
    assert FuzzySet(a)


@pytest.mark.parametrize("a", [(ac1, ac2)])
def test_fuzzy_set_same_alpha_cut(a: Iterable[AlphaCut]) -> None:
    with pytest.raises(ValueError, match="You have two Alpha-cuts with same level*"):
        assert FuzzySet(a)


@pytest.mark.parametrize("a", [ac1, ac2, ac3])
def test_add_alpha_cut_to_fuzzy_set_correct(a: AlphaCut) -> None:
    fs = FuzzySet([ac0])
    assert fs.add_alpha_cut(a) is fs


@pytest.mark.parametrize("a", [(ac2, ac0), (ac2, ac2)])
def test_add_alpha_cut_to_fuzzy_set_incorrect(a: AlphaCut | tuple[AlphaCut, ...]) -> None:
    with pytest.raises(ValueError, match="You have two Alpha-cuts with same level*"):
        fs = FuzzySet([ac0])
        fs.add_alpha_cut(a)


def test_remove_alpha_cut_from_fuzzy_set_correct() -> None:
    fs = FuzzySet([ac0, ac1, ac3])
    assert fs.remove_alpha_cut(0.01) is fs


@pytest.mark.parametrize("a", [.05, 0.6, 1.0, Decimal(0.9)])
def test_remove_alpha_cut_to_fuzzy_set_incorrect(a: float | Decimal) -> None:
    with pytest.raises(ValueError, match=r"There is no alpha-cut level (\d|.)+ in fuzzy set."):
        fs = FuzzySet([ac0, ac1, ac3])
        fs.remove_alpha_cut(a)


@pytest.mark.parametrize("a, ex", [(0.1, True), (.2, True), (.4, True), (1.0, False)])
def test_fuzy_set_membership_(a, ex) -> None:
    fs = FuzzySet([ac4, ac5, ac6])
    assert fs.check_membership_level(a) == ex


def test_check_alpha_level_membership_fuzzy_set_incorrect() -> None:
    with pytest.raises(ValueError, match=r"Fuzzy set obstructed!"):
        FuzzySet([ac0, ac1, ac3, ac7])


def test_from_points(points: Iterable[tuple[Numeric, Numeric]]) -> None:
    assert FuzzySet.from_points(tuple([0., 0.1, 0.2, 1.]), points)


def test_from_wrong_points(wrong_points: Iterable[tuple[Numeric, Numeric]]) -> None:
    with pytest.raises(ValueError, match=r"Fuzzy set domain obstructed."):
        FuzzySet.from_points(tuple([0., 0.1, 0.2, 1.]), wrong_points)


@pytest.mark.parametrize("fs1, fs2, tnorm, fsex", [(FuzzySet([AlphaCut(1.0, 0, 1)]),
                                                    FuzzySet([AlphaCut(1.0, 0, 1)]),
                                                    Min,
                                                    FuzzySet([AlphaCut(1.0, 0, 2)]),
                                                    )])
def test_fuzzy_set_add_with_tnorm(fs1, fs2, tnorm, fsex):
    assert fs1.add_with_tnorm(fs2, tnorm) == fsex


@pytest.mark.parametrize("fs1, fs2, tnorm, fsex", [(FuzzySet([AlphaCut(1.0, 0, 1)]),
                                                    FuzzySet([AlphaCut(1.0, 0, 1)]),
                                                    Min,
                                                    FuzzySet([AlphaCut(1.0, -1, 1)]),
                                                    )])
def test_fuzzy_set_sub_with_tnorm(fs1, fs2, tnorm, fsex):
    assert fs1.sub_with_tnorm(fs2, tnorm) == fsex


@pytest.mark.parametrize("fs1, res", [(FuzzySet([AlphaCut(1.0, 0, 1)]), True),
                                      (FuzzySet([AlphaCut(1.0, -1, 1)]), False),
                                      (cast(FuzzySet, 1), False)], )
def test_fuzzy_set__eq__(fs1, res):
    fs0 = FuzzySet([AlphaCut(1.0, 0, 1)])
    assert (fs0 == fs1) == res


def test_fuzzy_set_get_points_to_plot():
    fs = FuzzySet([AlphaCut(0.2, 1, 3)])
    points = fs.get_points_to_plot()
    assert points[0] == Alcs(0.2, 1.0, BorderSide.LEFT)
    assert points[1] == Alcs(0.2, 3.0, BorderSide.RIGHT)
    assert points[2] == Alcs(0.2, 1.0606060606060606, BorderSide.INSIDE)
