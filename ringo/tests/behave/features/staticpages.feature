Feature: Check general pages
  Will check if the genral pages of the ringo application are reachable

  Scenario: About page
    Given a anonymous user
     When opens the about page
     Then the user should get a 200 http response

  Scenario: Contact page
    Given a anonymous user
     When opens the contact page
     Then the user should get a 200 http response

  Scenario: Version page
    Given a anonymous user
     When opens the version page
     Then the user should get a 200 http response

  Scenario: Home page
    Given a anonymous user
     When opens the home page
     Then the user should get a 200 http response
