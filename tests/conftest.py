from pytest import fixture
from pytest_bdd import given, when, then, parsers, scenarios

from beancount.core.compare import hash_entry, includes_entries, excludes_entries
from beancount.loader import load_string
from beancount.parser import printer
from context import share

#
# Fixtures/steps used by all plugins
#
@fixture
def output_txns():
    """
    A fixture used by the when and then steps.
    Allows the "then" steps to access the output of the "when" step.

    Returns:
      A reference to an empty list.
    """
    return list()

#
# Fixtures/steps used by all plugins
#
@fixture
def errors():
    return list()

@given(parsers.parse('this config:'
                     '{config}'))
def config(config):
    return config

@given(parsers.parse('the following beancount transaction:'
                     '{input_txn_text}'))
def input_txns(input_txn_text):
    input_txns, _, _ = load_string(input_txn_text)
    assert len(input_txns) == 1  # Only one entry in feature file example
    return input_txns


@when(parsers.parse('this transaction is processed:'
                    '{input_txn_text}'))
def is_processed(input_txns, output_txns, errors, config, input_txn_text):
    input_txns, errors2, _ = load_string(input_txn_text)
    for error in errors2:
        print(printer.format_error(error))
    assert len(input_txns) == 1  # Only one entry in feature file example
    output_txns[:], errors[:] = share.share(input_txns, {}, config)
    for error in errors:
        print(printer.format_error(error))


@then(parsers.parse('the original transaction should be modified:'
                    '{correctly_modified_txn_text}'))
def original_txn_modified(output_txns, errors, correctly_modified_txn_text):
    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the first in the list of output transactions
    try:
        modified_txn = output_txns[0]
    except IndexError as error:
        raise error
    # Get correctly modified original transaction from feature file
    correctly_modified_txn = load_string(correctly_modified_txn_text)[0][0]

    # Compare strings instead of hashes because that's an easy way to exclude filename & lineno meta.

    try:
        # Remove arbitrary meta.
        for tx in (modified_txn, correctly_modified_txn):
            del tx.meta['filename']
            del tx.meta['lineno']
            for posting in tx.postings:
                if 'filename' in posting.meta:
                    del posting.meta['filename']
                if 'lineno' in posting.meta:
                    del posting.meta['lineno']
                if '__automatic__' in posting.meta:
                    del posting.meta['__automatic__']
                pass

        assert hash_entry(modified_txn) == hash_entry(correctly_modified_txn)

    except AssertionError:
        print("RECEIVED:", modified_txn)
        print("EXPECTED:", correctly_modified_txn)
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == correctly_modified_txn_text+'\n'
        # But in case strings matches..
        raise Exception("Transactions do not match, although their printed output is equal. See log output.")

@then(parsers.parse('the original transaction should not be modified'))
def tx_not_modified(input_txns, output_txns):
    original_txn = input_txns[0]
    modified_txn = output_txns[0]
    try:
        assert hash_entry(original_txn) == hash_entry(modified_txn)
    except AssertionError:
        print("RECEIVED:", modified_txn)
        print("EXPECTED:", original_txn)
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == printer.format_entry(original_txn)
        # But in case strings matches..
        raise Exception("Transactions do not match, although their printed output is equal. See log output.")



@then(parsers.parse('should produce error:\n'
                    '{exception_text}'))
def added_error(input_txns, errors, exception_text):
    original_txn = input_txns[0]
    assert len(errors) == 1
    expected_error = share.PluginShareParseError(original_txn.meta, exception_text, original_txn)
    assert type(errors[0]) is type(expected_error) and errors[0].message == expected_error.message and errors[0].entry == expected_error.entry
