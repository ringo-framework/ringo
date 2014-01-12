Feature: Check Login feature
  Will check login in the application

  Scenario: Login succeeds
    Given a anonymous user
     When opens the login page
     When submits valid login data
     Then the user should get a 302 http response

  Scenario: Login fails page
    Given a anonymous user
     When opens the login page
     When submits invalid login data
     Then the user should get a 200 http response
