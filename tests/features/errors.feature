Feature: Report meaningful errors

  Background: Simple case without config
    Given this config:
      {}

  Scenario: Throw Error if sharing a non-applicable posting (Assets, Liabilities or Equity)
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
          share: "Bob-4"
        Expenses:Food:Drinks

    Then the original transaction should not be modified
    And should produce error:
      Mark "share" doesn't make sense on a "Assets" type posting.

  Scenario: Throw Error if total shared absolute amount is greater than posting amount
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-6"
          share2: "Charlie-6"

    Then the original transaction should not be modified
    And should produce error:
        The posting can't share more than it's absolute value

  Scenario: Throw Error if total shared relative amount is greater than 100%
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-60%"
          share2: "Charlie-60%"

    Then the original transaction should not be modified
    And should produce error:
        The posting can't share more percent than 100%.

  Scenario: Throw Error if further sharing a posting whose amount is reduced to zero after sharing absolute amounts
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-10"
          share2: "Charlie-42%"

    Then the original transaction should not be modified
    And should produce error:
        It doesn't make sense to split a remaining amount of zero.

  Scenario: Throw Error if further sharing a posting whose amount is already shared by 100%
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Beer with my guy friends"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks
          share: "Bob-100%"
          share2: "Charlie"

    Then the original transaction should not be modified
    And should produce error:
        It doesn't make sense to further auto-split when amount is already split for full 100%.

  Scenario: Throw Error if sharing both Expense and Income postings
    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with my guy friends"
        Assets:Cash           -15.00 EUR
        Expenses:Food:Lunch    17.00 EUR
          share: "Bob"
        Income:Random          -2.00 EUR
          share: "Bob"

    Then the original transaction should not be modified
    And should produce error:
        Plugin "share" doesn't work on transactions that has both income and expense: please split it up into two transactions instead.
