Feature: Configure plugin behavior

  Scenario: Rename mark at tag

    Given this config:
      {"mark_name": "asdf"}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #asdf-Bob
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
          shared: "Assets:Debtors:Bob (50%, 5.00 USD)"
        Assets:Debtors:Bob          5.00 USD
          shared: "Expenses:Food:Drinks (50%, 5.00 USD)"

  Scenario: Rename mark at meta

    Given this config:
      {"mark_name": "asdf"}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        asdf: "Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
          shared: "Assets:Debtors:Bob (50%, 5.00 USD)"
        Assets:Debtors:Bob          5.00 USD
          shared: "Expenses:Food:Drinks (50%, 5.00 USD)"



  Scenario: Disable adding new meta

    Given this config:
      {"meta_name": None}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
        Assets:Debtors:Bob          5.00 USD

  Scenario: Rename added meta

    Given this config:
      {"meta_name": 'asdf'}

    When this transaction is processed:
      2020-01-01 * "BarAlice" "Lunch with friend Bob" #share-Bob
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks

    Then the original transaction should be modified:
      2020-01-01 * "BarAlice" "Lunch with friend Bob"
        Assets:Cash               -10.00 USD
        Expenses:Food:Drinks        5.00 USD
          asdf: "Assets:Debtors:Bob (50%, 5.00 USD)"
        Assets:Debtors:Bob          5.00 USD
          asdf: "Expenses:Food:Drinks (50%, 5.00 USD)"
