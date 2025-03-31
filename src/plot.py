import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import NamedTuple, Self

from src import fuzzy_set
from src.fuzzy_set import FuzzySet
from src.types import BorderSide


class FuzzyPlotDef(NamedTuple):
    fuzzy_set: FuzzySet
    label: str
    color: str


class FuzzyPlot:
    """
    Class to plot Fuzzy Sets.
    :param fpd: FuzzyPlotDef object. tuple with FuzzySet, label and color.
    """
    def __init__(self, fpd: FuzzyPlotDef | None = None):
        self.to_plot: list[FuzzyPlotDef] = [] if fpd is None else [fpd]

    def add_to_plotlist(self, fpd: FuzzyPlotDef) -> Self:
        """
        Method to add FuzzyPlotDef object to plot.
        :param fpd: FuzzyPlotDef object.
        :return: FuzzyPlot object.
        """
        self.to_plot.append(fpd)
        return self

    def plot(self, file: str | None = None) -> None:
        """
        Plot execution method.
        :param file: Filepath to save plot. If none file will not be saved.
        """
        legend = []

        def point_tick_typer(p: BorderSide) -> str:
            match p:
                case BorderSide.LEFT:
                    return "<"
                case BorderSide.RIGHT:
                    return ">"
                case BorderSide.INSIDE:
                    return ","

        for fpd in self.to_plot:
            for point in fpd.fuzzy_set.get_points_to_plot():
                plt.plot(point.coord,
                         point.alpha_level,
                         point_tick_typer(point.side),
                         color=fpd.color)
            legend.append(mpatches.Patch(color=fpd.color, label=fpd.label))

        plt.legend(handles=legend)
        plt.show()
        if file is not None:
            plt.savefig(file)
