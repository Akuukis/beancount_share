from pytest import fixture
from pytest_bdd import given, when, then, parsers, scenarios

from beancount.core.data import Transaction
from beancount.core.compare import hash_entry, includes_entries, excludes_entries
from beancount.loader import load_string
from beancount.parser import printer
from beancount_plugin_utils import metaset
from context import share

def strip_flaky_meta(transaction: Transaction):
    transaction = transaction._replace(meta=metaset.discard(transaction.meta, 'filename'))
    transaction = transaction._replace(meta=metaset.discard(transaction.meta, 'lineno'))
    # new_postings = list(tx.postings)
    for j,_ in enumerate(transaction.postings):
        transaction.postings[j] = transaction.postings[j]._replace(meta=metaset.discard(transaction.postings[j].meta, 'filename'))
        transaction.postings[j] = transaction.postings[j]._replace(meta=metaset.discard(transaction.postings[j].meta, 'lineno'))
        transaction.postings[j] = transaction.postings[j]._replace(meta=metaset.discard(transaction.postings[j].meta, '__automatic__'))
    # transaction._replace(postings=new_postings)

    return transaction


@fixture
def config():
    return ""

@fixture
def output_txns():
    """
    A fixture used by the when and then steps.
    Allows the "then" steps to access the output of the "when" step.

    Returns:
      A reference to an empty list.
    """
    return list()

@fixture
def errors():
    return list()

@given(parsers.parse('this config:'
                     '{config}'))
def config_custom(config):
    pass

@given(parsers.parse('the following setup:'
                     '{setup_txns_text}'))
def setup_txns(setup_txns_text):
    return setup_txns_text

@given(parsers.parse('the following beancount transaction:'
                     '{input_txn_text}'))
def input_txns(input_txn_text):
    input_txns, _, _ = load_string(input_txn_text)
    assert len(input_txns) == 1  # Only one entry in feature file example
    return input_txns


@when(parsers.parse('this transaction is processed:'
                    '{input_txn_text}'))
def is_processed(input_txns, errors, config, input_txn_text, setup_txns_text, output_txns):
    text = 'plugin "beancount_share.share" "' + config.strip('\n') + '"\n' + setup_txns_text + input_txn_text
    print('\nInput (full & raw):\n------------------------------------------------\n' + text + '\n')
    output_txns[:], errors[:], _ = load_string(text)
    print('\nOutput (Transactions):\n------------------------------------------------\n')
    for txn in output_txns:
        print(printer.format_entry(txn))
    print('\nOutput (Errors):\n------------------------------------------------\n')
    for error in errors:
        print(printer.format_error(error))


@then(parsers.parse('the original transaction should be modified:'
                    '{correctly_modified_txn_text}'))
def original_txn_modified(output_txns, errors, correctly_modified_txn_text):
    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the last in the list of output transactions
    try:
        modified_txn = strip_flaky_meta(output_txns[-1])
    except IndexError as error:
        raise error
    # Get correctly modified original transaction from feature file
    correctly_modified_txn = strip_flaky_meta(load_string(correctly_modified_txn_text)[0][-1])

    print(" ; RECEIVED:\n", printer.format_entry(modified_txn))
    print(" ; EXPECTED:\n", printer.format_entry(correctly_modified_txn))

    # Compare strings instead of hashes because that's an easy way to exclude filename & lineno meta.

    try:
        print("RECEIVED:\n", modified_txn)
        print("EXPECTED:\n", correctly_modified_txn)
        assert hash_entry(modified_txn) == hash_entry(correctly_modified_txn)

    except AssertionError:
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == '\n'+correctly_modified_txn_text+'\n'
        # But in case strings matches..
        raise Exception("Transactions do not match, although their printed output is equal. See log output.")

@then(parsers.parse('the original transaction should not be modified'))
def tx_not_modified(input_txns, output_txns):
    original_txn = strip_flaky_meta(input_txns[-1])
    modified_txn = strip_flaky_meta(output_txns[-1])
    try:
        assert hash_entry(original_txn) == hash_entry(modified_txn)
    except AssertionError:
        print("RECEIVED:", modified_txn)
        print("EXPECTED:", original_txn)
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == printer.format_entry(original_txn)
        # But in case strings matches..
        raise Exception("Transactions do not match, although their printed output is equal. See log output.")



@then(parsers.parse('should not error'))
def not_error(errors):
    assert len(errors) == 0

@then(parsers.parse('should produce config error:'
                    '{exception_text}'))
def config_error(input_txns, errors, exception_text):
    original_txn = input_txns[-1]
    assert len(errors) == 1
    expected_error = share.PluginShareParseError(original_txn.meta, exception_text.strip('\n'), original_txn)
    assert type(errors[0]) is type(expected_error)
    assert errors[0].message == expected_error.message
    assert errors[0].entry == None

@then(parsers.parse('should produce plugin error:'
                    '{exception_text}'))
def plugin_error(input_txns, errors, exception_text):
    original_txn = input_txns[-1]
    assert len(errors) == 1
    expected_error = share.PluginShareParseError(original_txn.meta, exception_text.strip('\n'), original_txn)
    assert type(errors[0]) is type(expected_error)
    assert errors[0].message == expected_error.message
    assert strip_flaky_meta(errors[0].entry) == strip_flaky_meta(expected_error.entry)

@then(parsers.parse('should produce beancount error:'
                    '{exception_text}'))
def beancount_error(input_txns, errors, exception_text, output_txns):
    original_txn = input_txns[-1]
    modified_txn = output_txns[-1]
    assert len(errors) == 1
    expected_error = share.PluginShareParseError(original_txn.meta, exception_text.strip('\n'), original_txn)
    assert errors[0].message == expected_error.message and errors[0].entry == modified_txn
