from typing import List, Set, Union, Tuple
from copy import deepcopy

from beancount.core.data import Transaction, Posting
from beancount.core.inventory import Inventory


def read_config(config_string):
    """
    Args:
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A dict of the configuration string.
    """
    if len(config_string) == 0:
        config_obj = {}
    else:
        config_obj = eval(config_string, {}, {})

    if not isinstance(config_obj, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    return config_obj

def extract_marks(target: Union[Transaction, Posting], mark: str) -> Tuple[Set[str], Union[Transaction, Posting]]:
    copy = deepcopy(target)

    marks = [(k,v) for k,v in copy.meta.items() if k[0:len(mark)] == mark and set(k[len(mark):]) <= DIGITS_SET]
    for k,_ in marks:
        del copy.meta[k]

    return [mark for _,mark in marks], copy

MARK_SEPERATOR = '-'
DIGITS_SET = set(['0','1','2','3','4','5','6','7','8','9'])
def normalize_marked_txn(_tx: Transaction, mark_name: str):
    """
    If a transaction is marked, hoist marked tags into transation meta(s).

    Args:
        txs [Transaction]: transaction instances.
        mark_name [str]: the mark.
    Return:
        Transaction with normalized marks.
    """

    tx = deepcopy(_tx)

    for tag in tx.tags:
        if tag == mark_name or tag[0:len(mark_name+MARK_SEPERATOR)] == mark_name+MARK_SEPERATOR:
            tx = tx._replace(
                tags=tx.tags.difference([tag])
            )
            mark_name = mark_name + ('' if not (mark_name in tx.meta) else str(900 + len([k for k in tx.meta if k[0:len(mark_name)] == mark_name and set(k[len(mark_name):]) <= DIGITS_SET])))
            tx.meta.update({mark_name: tag[len(mark_name+MARK_SEPERATOR):] or ''})

    return tx


DEFAULT_APPLICABLE_ACCOUNT_TYPES = set(["Income", "Expenses", "Assets", "Liabilities", "Equity"])

def marked_postings(
        tx: Transaction,
        mark_name: str,
        applicable_account_types: Set[str] = DEFAULT_APPLICABLE_ACCOUNT_TYPES,
        allow_posting_level_mark: bool = True
    ):
    """
    Iterates over postings of the transaction, returning most specific mark value for applicable account types.

    Args:
        tx [Transaction]: transaction instance.
        mark_name [str]: the mark.
        applicable_account_types [Set[str]]: set of account types that must be considered, defaults to all five.
        allow_posting_level_mark [bool]: set to False if posting-level marks should raise error instead.
    Yields:
        list of mark values or None.
        posting.
        original posting.
    """

    default_mark_pairs: List[Tuple[str, str]] = [(k,v) for k,v in tx.meta.items() if k[0:len(mark_name)] == mark_name and set(k[len(mark_name):]) <= DIGITS_SET]
    for k,_ in default_mark_pairs:
        del tx.meta[k]

    for _posting in tx.postings:
        marks, posting = extract_marks(_posting, mark_name)

        if(len(marks) > 0):
            yield marks, posting, _posting
        elif(len(default_mark_pairs) > 0):
            if(posting.account.split(':')[0] not in applicable_account_types):
                yield None, posting, _posting
            else:
                yield [v for _,v in default_mark_pairs], posting, _posting
        else:
            yield None, posting, _posting

def sum_income(tx: Transaction) -> Inventory:
    total = Inventory()
    for posting in tx.postings:
        if(posting.account.split(':')[0] == "Income"):
            total.add_position(posting)
    return total

def sum_expenses(tx: Transaction) -> Inventory:
    total = Inventory()
    for posting in tx.postings:
        if(posting.account.split(':')[0] == "Expenses"):
            total.add_position(posting)
    return total

