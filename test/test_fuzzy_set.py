from decimal import Decimal
from typing import Iterable

from src.fuzzy_set import AlphaCut, FuzzySet
import pytest

# TODO [ KM 5 ] Zastanowilbym sie nad przygotowaniem fixture dla ponizszych obiektow
#  a nie osadzal je globalnie w tym miejscu.
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


# TODO [ KM 6 ]
#  Odnosnie pytania o testowanie wykresow.

#  Podejscie 1
#  Zawsze, kiedy funkcja wykonuje pewne operacje "zewnetrzne" mozna sprawdzic, czy zostala wywolana bez wyjatkow
#  i jesli zleca wykonanie pewnych operacji zewnetrznej bibliotece, przyjac ze to juz jest ok i samo wywolanie
#  bez bledow jest ok. Mozna tez sprawdzic czy we wskazanej lokalizacji (testowej) znajduje sie plik o wymaganej 
#  nazwie i rozszerzeniu.

#  Podejscie 2
#  Kiedy uzywamy matplotlib, mozna przechwycic elementy wykresu, ktore sa obiektami i sprawdzac ich strukture
#  Przyklad:

#  import matplotlib.pyplot as plt
#  import numpy as np

#  def generate_plot() -> tuple[matplotlib.figure.Figure, matplotlib.axes._axes.Axes]:
#     fig, ax = plt.subplots()
#     x = np.array([1, 2, 3])
#     y = np.array([4, 5, 6])
#     ax.plot(x, y)
#     return fig, ax 

#  def test_plot_data() -> None:
    # fig, ax = generate_plot()
    
    # line = ax.lines[0]
    # x_data = line.get_xdata()
    
    # assert list(x_data) == [1, 2, 3]

    # plt.close(fig)  # Zamykamy wykres, aby nie wyświetlał się w tle

# Podejscie 3
# Mozna stosowac dedykowane biblioteki / pluginy, np. pytest-mpl
# https://github.com/matplotlib/pytest-mpl

# Jest kilka mozliwosci, w zaleznosci od tego jak szczegolowo chcemy wejsc w temat.
