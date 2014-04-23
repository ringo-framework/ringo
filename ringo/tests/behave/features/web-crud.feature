Feature: Default GET requests of various actions of the modules.
  Will check if the basic default GET requests on the CRUD operations for
  different modules are working.

  Scenario Outline: List GET
    Given a <role> user
     When calls the overview web-url of modul <modul>
     Then the user should get a <response> http response

  Examples: User
  | role      | modul  | response |
  | anonymous | users  | 403      |
  | admin     | users  | 200      |
  | anonymous | usergroup | 403      |
  | admin     | usergroup | 200      |
  | anonymous | role  | 403      |
  | admin     | role  | 200      |
  | anonymous | profil | 403      |
  | admin     | profil | 200      |
  | anonymous | modul  | 403      |
  | admin     | modul  | 200      |
  | anonymous | appointment  | 403      |
  | admin     | appointment  | 200      |
  | anonymous | file  | 403      |
  | admin     | file  | 200      |
  | anonymous | news  | 403      |
  | admin     | news  | 200      |
  | anonymous | comments  | 403      |
  | admin     | comments  | 200      |
  | anonymous | tags  | 403      |
  | admin     | tags  | 200      |
  | anonymous | todos  | 403      |
  | admin     | todos | 200      |


  Scenario Outline: Create GET
    Given a <role> user
     When calls the create web-url of modul <modul>
     Then the user should get a <response> http response

  Examples: Create GET
  | role      | modul  | response |
  | anonymous | users  | 403      |
  | admin     | users  | 200      |
  | anonymous | usergroup | 403      |
  | admin     | usergroup | 200      |
  | anonymous | role  | 403      |
  | admin     | role  | 200      |
  | anonymous | profil | 404      |
  | admin     | profil | 404      |
  | anonymous | modul  | 404      |
  | admin     | modul  | 404      |
  | anonymous | appointment  | 403      |
  | admin     | appointment  | 200      |
  | anonymous | file  | 403      |
  | admin     | file  | 200      |
  | anonymous | news  | 403      |
  | admin     | news  | 200      |
  | anonymous | comments  | 403      |
  | admin     | comments  | 200      |
  | anonymous | tags  | 403      |
  | admin     | tags  | 200      |
  | anonymous | todos  | 403      |
  | admin     | todos | 200      |

  Scenario Outline: Read GET
    Given a <role> user
     When calls the read web-url for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Read GET
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |
  | admin     | user  | 99  | 400 |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |
  | anonymous | profil | 1  | 403      |
  | admin     | profil | 1  | 200      |
  | anonymous | modul  | 1  | 403      |
  | admin     | modul  | 1  | 200      |
  | anonymous | appointment  | 1  | 403      |
  | admin     | appointment  | 1  | 400      |
  | anonymous | file  | 1  | 403      |
  | admin     | file  | 1  | 400      |
  | anonymous | news  | 1  | 403      |
  | admin     | news  | 1  | 400      |
  | anonymous | comments  | 1  | 403      |
  | admin     | comments  | 1  | 400      |
  | anonymous | tags  | 1  | 403      |
  | admin     | tags  | 1  | 400      |
  | anonymous | todos  | 1  | 403      |
  | admin     | todos  | 1  | 400      |

  Scenario Outline: Edit GET
    Given a <role> user
     When calls the edit web-url for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Edit GET
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |
  | anonymous | profil | 1  | 403      |
  | admin     | profil | 1  | 200      |
  | anonymous | modul  | 1  | 403      |
  | admin     | modul  | 1  | 200      |
  | anonymous | appointment  | 1  | 403      |
  | admin     | appointment  | 1  | 400      |
  | anonymous | file  | 1  | 403      |
  | admin     | file  | 1  | 400      |
  | anonymous | news  | 1  | 403      |
  | admin     | news  | 1  | 400      |
  | anonymous | comments  | 1  | 403      |
  | admin     | comments  | 1  | 400      |
  | anonymous | tags  | 1  | 403      |
  | admin     | tags  | 1  | 400      |
  | anonymous | todos  | 1  | 403      |
  | admin     | todos  | 1  | 400      |

  Scenario Outline: Delete GET
    Given a <role> user
     When calls the delete web-url for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Delete GET
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |
  | anonymous | profil | 1  | 404      |
  | admin     | profil | 1  | 404      |
  | anonymous | modul  | 1  | 404      |
  | admin     | modul  | 1  | 404      |
  | anonymous | appointment  | 1  | 403      |
  | admin     | appointment  | 1  | 400      |
  | anonymous | file  | 1  | 403      |
  | admin     | file  | 1  | 400      |
  | anonymous | news  | 1  | 403      |
  | admin     | news  | 1  | 400      |
  | anonymous | comments  | 1  | 403      |
  | admin     | comments  | 1  | 400      |
  | anonymous | tags  | 1  | 403      |
  | admin     | tags  | 1  | 400      |
  | anonymous | todos  | 1  | 403      |
  | admin     | todos  | 1  | 400      |

  Scenario Outline: Export GET
    Given a <role> user
     When calls the export web-url for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Export GET
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |
  | anonymous | profil | 1  | 403      |
  | admin     | profil | 1  | 200      |
  | anonymous | modul  | 1  | 404      |
  | admin     | modul  | 1  | 404      |

  Scenario Outline: Import GET
    Given a <role> user
     When calls the import web-url for modul <modul>
     Then the user should get a <response> http response

  Examples: Import GET
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |
  | anonymous | profil | 1  | 403      |
  | admin     | profil | 1  | 200      |
  | anonymous | modul  | 1  | 404      |
  | admin     | modul  | 1  | 404      |
  | anonymous | appointment  | 1  | 403      |
  | admin     | appointment  | 1  | 200      |
  | anonymous | file  | 1  | 403      |
  | admin     | file  | 1  | 200      |
  | anonymous | news  | 1  | 403      |
  | admin     | news  | 1  | 200      |
  | anonymous | comments  | 1  | 403      |
  | admin     | comments  | 1  | 200 |
  | anonymous | tags  | 1  | 403      |
  | admin     | tags  | 1  | 200 |
  | anonymous | todos  | 1  | 403      |
  | admin     | todos  | 1  | 200 |
