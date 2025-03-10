from decimal import Decimal
from typing import Iterable

from src.fuzzy_set import AlphaCut, FuzzySet
import pytest

ac0 = AlphaCut(0.01, 0.0, 1.0)
ac1 = AlphaCut(0.1, 0.0, 1.0)
ac2 = AlphaCut(0.1, 0.0, 1.0)
ac3 = AlphaCut(0.3, 0.0, 1.0)

@pytest.mark.parametrize("a", [ac1, [ac2], [ac3]])
def test_fuzzy_set(a: Iterable[AlphaCut]) -> None:
    assert FuzzySet(a)

@pytest.mark.parametrize("a", [(ac1, ac2)])
def test_fuzzy_set_same_alpha_cut(a: Iterable[AlphaCut]) -> None:
    with pytest.raises(ValueError, match="You have two Alpha-cuts with same level*" ):
        assert FuzzySet(a)

@pytest.mark.parametrize("a", [ac1, ac2, ac3])
def test_add_alpha_cut_to_fuzzy_set_correct(a: AlphaCut) -> None:
    fs = FuzzySet([ac0])
    assert fs.add_alpha_cut(a) is fs

@pytest.mark.parametrize("a", [(ac2, ac0), (ac2, ac2)])
def test_add_alpha_cut_to_fuzzy_set_incorrect(a: AlphaCut | tuple[AlphaCut, ...]) -> None:
    with pytest.raises(ValueError, match="You have two Alpha-cuts with same level*" ):
        fs = FuzzySet([ac0])
        fs.add_alpha_cut(a)

@pytest.mark.parametrize("a", [0.01, 0.1, 0.3])
def test_remove_alpha_cut_from_fuzzy_set_correct(a: float) -> None:
    fs = FuzzySet([ac0, ac1, ac3])
    assert fs.remove_alpha_cut(0.01) is fs

@pytest.mark.parametrize("a", [.05, 0.6, 1, Decimal(0.9)])
def test_remove_alpha_cut_to_fuzzy_set_incorrect(a: float | Decimal) -> None:
    with pytest.raises(ValueError, match=r"There is no alpha-cut level (\d|.)+ in fuzzy set." ):
        fs = FuzzySet([ac0, ac1, ac3])
        fs.remove_alpha_cut(a)
