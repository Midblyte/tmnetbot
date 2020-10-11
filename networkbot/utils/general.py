from typing import Callable, Iterable


def evaluate(var_or_func, *args, **kwargs):
    return var_or_func(*args, **kwargs) if isinstance(var_or_func, Callable) else var_or_func


def args_joiner(*args, separator='_'):
    return separator.join(map(str, args))


def extract_args(data: str, args_number, fn = str) -> Iterable:
    return map(fn, data.rsplit('_', args_number)[-args_number:])
