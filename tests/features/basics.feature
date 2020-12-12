Feature: Basics

  Background: default
    Given this config:
      {}
    Given the following setup:
      2020-01-01 open Assets:Cash
      2020-01-01 open Assets:Safe
      2020-01-01 open Expenses:Food:Drinks
      2020-01-01 open Income:Random

  Scenario: Skip unmarked transactions.
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should not be modified
    Then should not error

  Scenario: Skip unmarked transactions even if they have both income nor expense.
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Income:Random         -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should not be modified
    Then should not error

  Scenario: Skip unmarked transactions even if they have no income nor expense.
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash           -10.00 EUR
        Assets:Safe

    Then the original transaction should not be modified
    Then should not error
