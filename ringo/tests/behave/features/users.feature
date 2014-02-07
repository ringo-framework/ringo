Feature: Check POST requests of the users module.
  Will check if the basic default POST requests on the CRUD operations for
  the users are working.

  Scenario Outline: Create POST
    Given a <role> user
     When calls the create web-url of modul <modul>
     When submits data (<error>) to create a item of modul <modul>
     Then the user should get a <response> http response

  Examples: Create valid POST
  | role      | modul | response | error              |
  | admin     | users  | 200      | password-missmatch |
  | admin     | users  | 200      | missing-login |
  | admin     | users  | 302      | none |

  Scenario Outline: Edit POST
    Given a <role> user
     When calls the edit web-url for item <id> of modul <modul>
     When submits data (<error>) to edit item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Create valid POST
  | role      | modul  | id | response | error              |
  | admin     | users  | 2  | 200      | missing-login |
  | admin     | users  | 2  | 302      | none |

  Scenario Outline: Delete POST
    Given a <role> user
     When calls the delete web-url for item <id> of modul <modul>
     When confirms deletion for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Delete POST
  | role      | modul | id | response |
  | admin     | user  | 2  | 302      |
