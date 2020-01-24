Feature: Make transactions
  As an account holder
  In order to keep my money nice and safe
  I want to deposit it into and withdraw it from my account

  Scenario: Successful deposit
    Given there is a customer "David Beckham"
    And "David Beckham" has a new account
    When I deposit 50 the account
    When I withdraw 20 the account
    Then then balance of the account should be 30
