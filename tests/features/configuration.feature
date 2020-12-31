Feature: Configure plugin behavior

  Background: default
    Given the following setup:
      2020-01-01 open Assets:Cash
      2020-01-01 open Expenses:Food:Drinks
      2020-01-01 open Income:Random

  Scenario: Handle default configuration

    Given this config:
      {
        'mark_name': 'share',
        'meta_name': 'shared',
        'account_debtors': 'Assets:Debtors',
        'account_creditors': 'Liabilities:Creditors',
        'open_date': '1970-01-01',
        'quantize': '0.01'
      }

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob      5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Throw Error if bad config provided

    Given this config:
      'I am not an object'

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should not be modified
    And should produce config error:
      Plugin configuration must be a dict, skipping.. The config: 'I am not an object'

  Scenario: Throw Error if bad date in the config provided

    Given this config:
      {'open_date': 'I am not an UTC date'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should not be modified
    And should produce config error:
      Bad "open_date" value - it must be a valid date, formatted in UTC (e.g. "2000-01-01").

  Scenario: Throw Error if bad quantize in the config provided

    Given this config:
      {'quantize': 'I am not an decimal value'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should not be modified
    And should produce config error:
      Bad "quantize" value - it must be a string that represents a decimal value (e.g. "0.01").

  Scenario: Rename mark at tag

    Given this config:
      {'mark_name': 'asdf'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #asdf-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Rename mark at meta

    Given this config:
      {'mark_name': 'asdf'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        asdf: "Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Disable adding new meta

    Given this config:
      {'meta_name': None}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
        Assets:Debtors:Bob          5.00 EUR

  Scenario: Rename added meta

    Given this config:
      {'meta_name': 'asdf'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          asdf: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          asdf: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Rename debtor account

    Given this config:
      {'account_debtors': 'Assets:EUR:Debtors'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:EUR:Debtors:Bob (50%, 5.00 EUR)"
        Assets:EUR:Debtors:Bob      5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Rename debtor account

    Given this config:
      {'account_creditors': 'Liabilities:EUR:Creditors'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Found change on floor with Bob"
        Assets:Cash                10.00 EUR
        Income:Random
          share: "Bob-40%"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Found change on floor with Bob"
        Assets:Cash                       10.00 EUR
        Income:Random                     -6.00 EUR
          shared: "Liabilities:EUR:Creditors:Bob 40% (-4.00 EUR)"
        Liabilities:EUR:Creditors:Bob     -4.00 EUR
          shared: "Income:Random 40% (-4.00 EUR)"

  Scenario: Disable creation open entries

    Given this config:
      {'open_date': None}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

    Then should produce beancount error:
      Invalid reference to unknown account 'Assets:Debtors:Bob'
