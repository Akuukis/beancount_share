from pytest import fixture
from pytest_bdd import scenario, given, when, then, parsers

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


@given(parsers.parse('the following beancount transaction:'
                     '{input_txn_text}'))
def input_txns(input_txn_text):
    input_txns, _, _ = load_string(input_txn_text)
    assert len(input_txns) == 1  # Only one entry in feature file example
    return input_txns

@then(parsers.parse('the original transaction should be modified:'
                    '{correctly_modified_txn_text}'))
def original_txn_modified(output_txns, correctly_modified_txn_text):

    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the first in the list of output transactions
    modified_txn = output_txns[0]

    # Get correctly modified original transaction from feature file
    correctly_modified_txn = load_string(correctly_modified_txn_text)[0][0]

    try:
        assert hash_entry(modified_txn, True) == hash_entry(correctly_modified_txn, True)
    except AssertionError:
        raise AssertionError('\n'+
            '\n; RECEIVED:\n'+printer.format_entry(modified_txn)+
            '\n; EXPECTED:\n'+printer.format_entry(correctly_modified_txn)
        )

#
# Scenarios/steps
#
@scenario('share.feature', 'Beancount docs example')
def test_blais_example():
    pass

@when(parsers.parse('the beancount_share plugin is executed with config:'
                    '{config}'))
def recur_txn(output_txns, input_txns, config):
    print(config)
    output_txns[:], _ = share.share(input_txns, {}, config)

@scenario('share.feature', 'Readme example')
def test_readme_example():
    pass
