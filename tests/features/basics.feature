Feature: Basics

    Background: default
        Given this config:
            {}
        Given the following setup:
            2020-01-01 open Assets:Cash
            2020-01-01 open Expenses:Food:Drinks

    Scenario: Leaves transaction links intact
