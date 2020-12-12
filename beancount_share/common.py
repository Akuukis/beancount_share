from typing import List, Set, Union, Tuple

from beancount.core.data import Transaction, Posting
from beancount.core.inventory import Inventory

import beancount_share.metaset as metaset

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

MARK_SEPERATOR = '-'
def normalize_marked_txn(tx: Transaction, mark_name: str):
    """
    If a transaction is marked, hoist marked tags into transation meta(s).

    Args:
        txs [Transaction]: transaction instances.
        mark_name [str]: the mark.
    Return:
        Transaction with normalized marks.
    """
    for tag in tx.tags:
        if tag == mark_name or tag[0:len(mark_name+MARK_SEPERATOR)] == mark_name+MARK_SEPERATOR:
            tx = tx._replace(
                tags=tx.tags.difference([tag]),
                meta=metaset.add(tx.meta, mark_name, tag[len(mark_name+MARK_SEPERATOR):] or ''),
            )

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
        original transaction.
    """

    default_marks = metaset.get(tx.meta, mark_name)
    tx = tx._replace(
        meta=metaset.clear(tx.meta, mark_name)
    )

    for _posting in tx.postings:
        marks = metaset.get(_posting.meta, mark_name)
        posting = _posting._replace(
            meta=metaset.clear(_posting.meta, mark_name)
        )

        if(len(marks) > 0):
            yield marks, posting, _posting, tx
        elif(len(default_marks) > 0):
            if(posting.account.split(':')[0] not in applicable_account_types):
                yield None, posting, _posting, tx
            else:
                yield default_marks, posting, _posting, tx
        else:
            yield None, posting, _posting, tx

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

