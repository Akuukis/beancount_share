Feature: Share expenses with other people easily

  Background: default

  Scenario: Example in this Readme

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

  Scenario: Carolyn example in Beancount docs

    Given this config:
      {
        'account_debtors': 'Assets:US:Share',
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
          shared: "Assets:US:Share:Carolyn 40% (13.06 USD)"
        Assets:US:Share:Carolyn        13.06 USD
          shared: "Expenses:Food:Grocery 40% (13.06 USD)"

  Scenario: Kyle example in Beancount docs

    Given this config:
      {
        'account_debtors': 'Expenses',
      }
    Given the following setup:
      2018-01-01 open Liabilities:US:Amex:BlueCash
      2018-01-01 open Expenses:Pharmacy

    When this transaction is processed:
      2019-02-01 * "AMAZON.COM" "MERCHANDISE - Diapers size 4 for Kyle" #share-Kyle-100p
        Liabilities:US:Amex:BlueCash  -49.99 USD
        Expenses:Pharmacy

    Then should not error
    Then the original transaction should be modified:
      2019-02-01 * "AMAZON.COM" "MERCHANDISE - Diapers size 4 for Kyle"
        Liabilities:US:Amex:BlueCash  -49.99 USD
        Expenses:Pharmacy               0.00 USD
          shared: "Expenses:Kyle 100% (49.99 USD)"
        Expenses:Kyle                   49.99 USD
          shared: "Expenses:Pharmacy 100% (49.99 USD)"


  Scenario: Bug #1 - handle padding
    Given the following setup:
      2020-01-01 open Equity:Opening-Balances CHF
      2020-01-01 open Assets:Bank CHF
      2020-01-01 open Assets:Savings CHF
      2020-01-01 pad Assets:Bank Equity:Opening-Balances
      2020-02-02 balance Assets:Bank 2000 CHF

    When this transaction is processed:
      2020-11-17 * "Savings"
        Assets:Savings         1000 CHF
        Assets:Bank           -1000 CHF

    Then should not error
