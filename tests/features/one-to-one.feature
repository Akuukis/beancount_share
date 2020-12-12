Feature: Share a single posting to single account

  Background: default
    Given this config:
      {}
    Given the following setup:
      2020-01-01 open Assets:Cash
      2020-01-01 open Expenses:Food:Drinks
      2020-01-01 open Expenses:Food:Snacks
      2020-01-01 open Income:RandomVeryVeryLong

  Scenario: Partially share sole Expense posting using absolute amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks
          share: "Assets:Debtors:Bob-4"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    6.00 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
        Assets:Debtors:Bob      4.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"

  Scenario: Partially share sole Expense posting with short account name
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-4"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    6.00 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
        Assets:Debtors:Bob      4.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"

  Scenario: Partially share sole Expense posting using relative amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-40%"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks    6.00 EUR
          shared: "Assets:Debtors:Bob 40% (4.00 EUR)"
        Assets:Debtors:Bob      4.00 EUR
          shared: "Expenses:Food:Drinks 40% (4.00 EUR)"

  Scenario: Partially share sole Expense posting using ommitted amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Fully share sole Expense posting using absolute amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-10"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        0.00 EUR
          shared: "Assets:Debtors:Bob 10.00 EUR"
        Assets:Debtors:Bob         10.00 EUR
          shared: "Expenses:Food:Drinks 10.00 EUR"

  Scenario: Fully share sole Expense posting using relative amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-100%"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        0.00 EUR
          shared: "Assets:Debtors:Bob 100% (10.00 EUR)"
        Assets:Debtors:Bob         10.00 EUR
          shared: "Expenses:Food:Drinks 100% (10.00 EUR)"

  Scenario: Share sole Income posting
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Found change on floor with Bob"
        Assets:Cash                10.00 EUR
        Income:RandomVeryVeryLong
          share: "Bob-40%"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Found change on floor with Bob"
        Assets:Cash                10.00 EUR
        Income:RandomVeryVeryLong              -6.00 EUR
          shared: "Liabilities:Creditors:Bob 40% (-4.00 EUR)"
        Liabilities:Creditors:Bob         -4.00 EUR
          shared: "Income:RandomVeryVeryLong 40% (-4.00 EUR)"

  Scenario: Share one of several postings
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -12.00 EUR
        Expenses:Food:Snacks        2.00 EUR
        Expenses:Food:Drinks
          share: "Assets:Debtors:Bob-4"

    Then should not error
    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -12.00 EUR
        Expenses:Food:Snacks        2.00 EUR
        Expenses:Food:Drinks        6.00 EUR
          shared: "Assets:Debtors:Bob 4.00 EUR"
        Assets:Debtors:Bob          4.00 EUR
          shared: "Expenses:Food:Drinks 4.00 EUR"
