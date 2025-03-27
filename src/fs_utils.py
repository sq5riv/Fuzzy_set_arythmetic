import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from typing import Self
from typing import NamedTuple

from src.fs_types import BorderSide
from src.fuzzy_set import FuzzySet

class Fuzzyplotdef(NamedTuple):
    fuzzy_set: FuzzySet
    label: str
    color: str

class Fuzzy_plot:
    def __init__(self, fs: Fuzzyplotdef | None = None):
        self.to_plot: list[Fuzzyplotdef] = [] if fs is None else [fs]

    def add_to_plotlist(self, fs: Fuzzyplotdef) -> Self:
        self.to_plot.append(fs)
        return self

    def plot(self, file: str | None= None) -> None:
        legend = []
        def point_tick_typer(p: BorderSide) -> str:
            if p == BorderSide.LEFT:
                return "<"
            elif p == BorderSide.RIGHT:
                return ">"
            else:
                return ","
        for fpd in self.to_plot:
            for point in fpd.fuzzy_set.get_points_to_plot():
                plt.plot(point.coord,
                         point.alpha_level,
                         point_tick_typer(point.side),
                         color= fpd.color)
            legend.append(mpatches.Patch(color= fpd.color, label= fpd.label))

        plt.legend(handles=legend)
        plt.show()
        if file is not None:
            plt.savefig(file)
