Feature: Configure plugin behavior

  Scenario: Rename mark at tag

    Given this config:
      {"mark_name": "asdf"}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #asdf-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Rename mark at meta

    Given this config:
      {"mark_name": "asdf"}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        asdf: "Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"



  Scenario: Disable adding new meta

    Given this config:
      {"meta_name": None}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
        Assets:Debtors:Bob          5.00 EUR

  Scenario: Rename added meta

    Given this config:
      {"meta_name": 'asdf'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          asdf: "Assets:Debtors:Bob (50%, 5.00 EUR)"
        Assets:Debtors:Bob          5.00 EUR
          asdf: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Rename debtor account

    Given this config:
      {"account_debtors": "Assets:EUR:Debtors"}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 EUR
        Expenses:Food:Drinks        5.00 EUR
          shared: "Assets:EUR:Debtors:Bob (50%, 5.00 EUR)"
        Assets:EUR:Debtors:Bob      5.00 EUR
          shared: "Expenses:Food:Drinks (50%, 5.00 EUR)"

  Scenario: Rename debtor account

    Given this config:
      {"account_creditors": "Liabilities:EUR:Creditors"}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Found change on floor with Bob"
        Assets:Cash                10.00 EUR
        Income:Random
          share: "Bob-40%"

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Found change on floor with Bob"
        Assets:Cash                       10.00 EUR
        Income:Random                     -6.00 EUR
          shared: "Liabilities:EUR:Creditors:Bob 40% (-4.00 EUR)"
        Liabilities:EUR:Creditors:Bob     -4.00 EUR
          shared: "Income:Random 40% (-4.00 EUR)"
