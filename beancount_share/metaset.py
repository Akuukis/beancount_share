"""
Abstraction on top of beancount's meta `dict` to operate on set of values per single key.

Implements `set` operations, but immutable: `add`, `remove`, `discard`, `clear`

Implements new methods:
- `set` - overwrites with a new set.
- `get` - retrieves a set of values from meta.
- `reset` - tidy up suffixes.

Under the hood, each value is saved in a seperate key with unique suffix of digits. Order not guaranteed.
"""

from typing import List, Set, Union, Tuple
from copy import deepcopy

from beancount.core.data import Transaction, Posting, Meta
from beancount.core.inventory import Inventory

datatype_set = set
DIGITS_SET = datatype_set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])


def contains_key(key: str, meta: str):
    """
    Determines whenever given meta is a mark, which may or may not be suffixed with numbers.

    Truthy meta examples for key "share":
    - share
    - share0
    - share900

    Falsey meta examples for key "share":
    - asdf
    - 42share
    - share42asdf

    Args:
        key [str]: the key.
        meta [str]: the meta.
    Return:
        Bool
    """
    if key is meta:
        return True

    if meta[0 : len(key)] == key and datatype_set(meta[len(key) :]) <= DIGITS_SET:
        return True

    return False


def get(meta: Meta, key: str) -> Set[str]:
    return [v for k, v in meta.items() if contains_key(key, k)]


def add(meta: Meta, key: str, value: str) -> Meta:
    copy = deepcopy(meta)
    safe_key: str

    if not (key in meta):
        safe_key = key
    else:
        suffix: int = 900 + len([k for k in meta if contains_key(key, k)])
        safe_key = key + str(suffix)

    copy[safe_key] = value
    return copy


def discard(meta: Meta, key: str) -> Meta:
    copy = deepcopy(meta)

    if key in meta:
        del copy[key]

    return copy

## Not used for now. Disabled to not pollute coverage report.
# def remove(meta: Meta, key: str) -> Meta:
#     copy = deepcopy(meta)

#     del copy[key]

#     return copy


def clear(meta: Meta, key: str) -> Meta:
    copy = deepcopy(meta)

    for metakey in [k for k, _ in meta.items() if contains_key(key, k)]:
        del copy[metakey]

    return copy

## Not used for now. Disabled to not pollute coverage report.
# def set(meta: Meta, key: str, new_set: Set[str]) -> Meta:
#     copy = clear(meta, key)

#     for elem in new_set:
#         copy = add(meta, key, elem)

#     return copy

## Not used for now. Disabled to not pollute coverage report.
# def reset(meta: Meta, key: str) -> Meta:
#     elements = get(meta, key)

#     return set(meta, key, elements)
