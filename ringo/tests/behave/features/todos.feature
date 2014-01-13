Feature: Check POST requests of the todos module.
  Will check if the basic default POST requests on the CRUD operations for
  the todos module are working.

  Scenario Outline: Create POST
    Given a <role> user
     When calls the create web-url of modul <modul>
     When submits data (<error>) to create a item of modul todos
     Then the user should get a <response> http response

  Examples: Create valid POST
  | role      | modul | response | error              |
  | admin     | todos  | 200      | missing-field |
  | admin     | todos  | 200      | conditional-required|
  | admin     | todos  | 302      | none |

  Scenario Outline: Edit POST
    Given a <role> user
     When calls the edit web-url for item <id> of modul <modul>
     When submits data (<error>) to edit item <id> of modul todos
     Then the user should get a <response> http response

  Examples: Edit valid POST
  | role      | modul  | id | response | error              |
  | admin     | todos  | 1  | 200      | missing-field |
  | admin     | todos  | 1  | 200      | conditional-required|
  | admin     | todos  | 1  | 302      | none |

  Scenario Outline: Delete POST
    Given a <role> user
     When calls the delete web-url for item <id> of modul <modul>
     When confirms deletion for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Delete POST
  | role      | modul | id | response |
  | admin     | todos | 1  | 302      |
