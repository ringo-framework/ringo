@needs_mail_setup
Feature: Check Registration fetaure.
  Will check various aspects of the registration and forget password
  service

  Scenario: Registration succeeds
    Given a anonymous user
     When opens the registration page
     When submits valid registration data
     Then the user should get a 200 http respone

  Scenario: Registration fails
    Given a anonymous user
     When opens the registration page
     When submits valid registration data
     Then the user should get a 200 http respone

  Scenario: Request password succeeds
    Given a anonymous user
     When opens the password reminder page
     When submits valid userdata data
     Then the user should get a 302 http respone

  Scenario: Request password fails
    Given a anonymous user
     When opens the password reminder page
     When submits invalid userdata data
     Then the user should get a 302 http respone
