"""Miscellaneous utility functions for operations not specific to the API client."""

try:
    # functools are native in Python 3.2.3+
    from functools import lru_cache as memoize
except ImportError:
    from backports.functools_lru_cache import lru_cache as memoize
import re
from math import ceil

from api.client.constants import DATA_SERIES_UNIQUE_TYPES_ID


@memoize(maxsize=None)
def str_camel_to_snake(term):
    """Convert a string from camelCase to snake_case.

    Parameters
    ----------
    term : string
        A camelCase string
    Returns
    -------
    string
        A new snake_case string

    """
    return re.sub(
        "([a-z0-9])([A-Z])", r"\1_\2", re.sub("(.)([A-Z][a-z]+)", r"\1_\2", term)
    ).lower()


@memoize(maxsize=None)
def str_snake_to_camel(term):
    """Convert a string from snake_case to camelCase.

    Parameters
    ----------
    term : string

    Returns
    -------
    string

    """
    camel = term.split("_")
    return "".join(camel[:1] + list([x[0].upper() + x[1:] for x in camel[1:]]))


def dict_reformat_keys(obj, format_func):
    """Convert a dictionary's keys from one string format to another.

    Parameters
    ----------
    obj : dict
        A dictionary with keys that need to be reformatted
    format_func : function
        Will execute on each key on the dict

    Returns
    -------
    dict
        A new dictionary with formatted keys

    """
    return {format_func(key): value for key, value in obj.items()}


def list_chunk(arr, chunk_size=50):
    """Chunk an array into chunks of a given max length.

    Parameters
    ----------
    arr : list
    chunk_size : int, optional

    Returns
    -------
    list of lists

    """
    return [
        arr[i * chunk_size : (i + 1) * chunk_size]
        for i in range(int(ceil(len(arr) / float(chunk_size))))
    ]


def intersect(lhs_list, rhs_list):
    """Return the common elements of two lists

    Parameters
    ----------
    lhs_list : list
        A list of some type that can be compared using `in`
    rhs_list : list
        A list of some type that can be compared using `in`

    Returns
    -------
    list
        A list of common elements

    """
    return list(filter(lambda elem: elem in rhs_list, lhs_list))


def zip_selections(entity_ids, **optional_selections):
    """Take a list of entity_ids and optional named selections and create a "selections" dict

    Parameters
    ----------
    entity_ids : list of ints
        Must be in the order of DATA_SERIES_UNIQUE_TYPES_ID
    optional_selections : kwargs
        Additional options to be combined with entity selections. Like `insert_nulls`

    Returns
    -------
    dict

    """
    selection = dict(zip(DATA_SERIES_UNIQUE_TYPES_ID, entity_ids))

    # add optional pararms to selection
    for key, value in list(optional_selections.items()):
        if key not in DATA_SERIES_UNIQUE_TYPES_ID:
            selection[key] = value
    return selection
