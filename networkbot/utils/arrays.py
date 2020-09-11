from itertools import islice
from typing import Iterable, Any, Tuple


def chunk(iterable: Iterable[Any], size: int) -> Iterable[Tuple]:
    iter_copy = iter(iterable)
    return iter(lambda: tuple(islice(iter_copy, size)), ())
