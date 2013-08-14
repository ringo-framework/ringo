Feature: Check Login and Registration fetaure.
  Will check various aspects of the login, registration and forget password
  service

  Scenario: Login succeeds
    Given a anonymous user
     When opens the login page
     When submits valid login data
     Then the user should get a 302 http respone

  Scenario: Login fails page
    Given a anonymous user
     When opens the login page
     When submits invalid login data
     Then the user should get a 200 http respone

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
