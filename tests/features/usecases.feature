Feature: Share expenses with other people easily

  Background: default

  Scenario: Example in this Readme

    Given this config:
      {}
    Given the following setup:
      2020-01-01 open Assets:Cash
      2020-01-01 open Expenses:Food:Drinks

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
          shared: "Assets:Debtors:Bob (50%, 5.00 USD)"
        Assets:Debtors:Bob          5.00 USD
          shared: "Expenses:Food:Drinks (50%, 5.00 USD)"

  Scenario: Example in Beancount docs

    Given this config:
      {
        'account_debtors': 'Assets:US:Share',
        'meta_name': 'share',
      }
    Given the following setup:
      2018-01-01 open Liabilities:US:Amex:BlueCash
      2018-01-01 open Expenses:Food:Grocery

    When this transaction is processed:
      2018-12-23 * "WHISK" "Water refill" #share-Carolyn-40p
        Liabilities:US:Amex:BlueCash  -32.66 USD
        Expenses:Food:Grocery

    Then should not error
    Then the original transaction should be modified:
      2018-12-23 * "WHISK" "Water refill"
        Liabilities:US:Amex:BlueCash  -32.66 USD
        Expenses:Food:Grocery          19.60 USD
          share: "Assets:US:Share:Carolyn 40% (13.06 USD)"
        Assets:US:Share:Carolyn        13.06 USD
          share: "Expenses:Food:Grocery 40% (13.06 USD)"
