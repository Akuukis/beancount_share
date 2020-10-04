from typing import List, Set, Union

from beancount.core.data import Transaction, Posting


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

def extract_marks(target: Union[Transaction, Posting], mark: str) -> Set[str]:
    if 'meta' not in target:
        return set()
    else:
        return [v for k,v in target.meta.items() if k[0:len(mark)] == mark and set(k[len(mark):]) <= DIGITS_SET]

MARK_SEPERATOR = '-'
DIGITS_SET = set(['0','1','2','3','4','5','6','7','8','9'])
def normalized_marked_txns(txs: List[Transaction], mark: str):
    """
    If a transaction is marked, hoist marked tags into transation meta(s).

    Args:
        txs [Transaction]: transaction instances.
        mark [str]: the mark.
    Yields:
        iterator of normalized transactions.
    """

    for tx in txs:

        for i, tag in enumerate(tx.tags):
            if tag == mark or tag[0:len(mark+MARK_SEPERATOR)] == mark+MARK_SEPERATOR:
                tx.tags.remove(tag)

                mark_name = mark + str(900 + i)
                tx.meta.update({mark_name: tag[len(mark+MARK_SEPERATOR):] or ''})

        marks = [(k,v) for k,v in tx.meta.items() if k[0:len(mark)] == mark and set(k[len(mark):]) <= DIGITS_SET]
        if(len(marks) == 1 and marks[0] != mark):
            tx.meta.update({mark: tx.meta[marks[0][0]]})
            del tx.meta[marks[0][0]]

        yield tx


DEFAULT_APPLICABLE_ACCOUNT_TYPES = set("Income", "Expenses", "Assets", "Liabilities", "Equity")

def marked_postings(
        tx: Transaction,
        mark: str,
        applicable_account_types: Set[str] = DEFAULT_APPLICABLE_ACCOUNT_TYPES,
        allow_posting_level_mark: bool = True
    ):
    """
    Iterates over postings of the transaction, returning most specific mark value for applicable account types.

    Args:
        tx [Transaction]: transaction instance.
        mark [str]: the mark.
        applicable_account_types [Set[str]]: set of account types that must be considered, defaults to all five.
        allow_posting_level_mark [bool]: set to False if posting-level marks should raise error instead.
    Yields:
        list of mark values or None.
        posting.
    """

    default_marks = [(k,v) for k,v in tx.meta.items() if k[0:len(mark)] == mark and set(k[len(mark):]) <= DIGITS_SET]

    for posting in tx.postings:
        marks = extract_marks(posting, mark)

        if(posting.account.split(':')[0] not in applicable_account_types):
            yield None, posting
        elif(len(marks) > 0):
            if(allow_posting_level_mark):
                yield marks, posting
            else:
                raise Exception("Found forbidden meta \"{marks}\" on a posting.")
        elif(len(default_marks) > 0):
            yield default_marks, posting
        else:
            yield None, posting

