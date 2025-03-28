from math import sin
from typing import Iterable

import pytest

from src.fs_types import Numeric

@pytest.fixture()
def points() -> Iterable[tuple[Numeric, ...]]:
    return [tuple([int(i), abs(sin(i/20))]) for i in range(100)]

@pytest.fixture()
def wrong_points() -> Iterable[tuple[Numeric, ...]]:
    ret =  [tuple([int(i), abs(sin(i/20))]) for i in range(100)]
    ret.append(tuple([0, 100]))
    return ret