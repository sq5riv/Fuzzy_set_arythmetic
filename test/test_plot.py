from src.plot import FuzzyPlotDef, FuzzyPlot
from src.fuzzy_set import FuzzySet, AlphaCut


def test_fuzzyplotdef():
    fs = FuzzySet([AlphaCut(0.2, 1, 3)])
    fpd = FuzzyPlotDef(fs, 'My_set', "red")
    assert isinstance(fpd, FuzzyPlotDef)


def test_fuzzy_plot():
    fs = FuzzySet([AlphaCut(0.2, 1, 3)])
    fpd = FuzzyPlotDef(fs, 'My_set', "red")
    fp = FuzzyPlot(fpd)
    fp.plot('plot.jpg')


def test_fuzzy_plot_add_to_plot_list():
    fs = FuzzySet([AlphaCut(0.2, 1, 3)])
    fpd = FuzzyPlotDef(fs, 'My_set', "red")
    fp = FuzzyPlot(fpd)
    check_id = id(fp)
    fs2 = FuzzySet([AlphaCut(0.2, 1, 3)])
    fpd2 = FuzzyPlotDef(fs2, 'My_set2', "green")
    fp = fp.add_to_plotlist(fpd2)
    fs3 = FuzzySet([AlphaCut(0.2, 1, 3)])
    fpd3 = FuzzyPlotDef(fs3, 'My_set2', "green")
    fp = fp.add_to_plotlist(fpd3)
    assert check_id == id(fp)
