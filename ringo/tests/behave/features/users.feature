Feature: Check the user modul
  Will check if the basic CRUD operations for the user are working

  Scenario Outline: Create GET
    Given a <role> user
     When opens the create page of modul <modul>
     Then the user should get a <response> http response

  Examples: Get create page
  | role      | modul  | response |
  | anonymous | users  | 403      |
  | admin     | users  | 200      |

  Scenario Outline: Create POST
    Given a <role> user
     When opens the create page of modul <modul>
     When submits data (<error>) to create a item of modul <modul>
     Then the user should get a <response> http response

  Examples: Create valid POST
  | role      | modul | response | error              |
  | admin     | users  | 200      | password-missmatch |
  | admin     | users  | 200      | missing-login |
  | admin     | users  | 302      | none |

  Scenario Outline: Read GET
    Given a <role> user
     When opens the read page for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Get read page
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |

  Scenario Outline: Edit GET
    Given a <role> user
     When opens the edit page for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Edit GET
  | role      | modul | id | response |
  | anonymous | user  | 2  | 403      |
  | admin     | user  | 2  | 200      |

  Scenario Outline: Edit POST
    Given a <role> user
     When opens the edit page for item <id> of modul <modul>
     When submits data (<error>) to edit item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Create valid POST
  | role      | modul  | id | response | error              |
  | admin     | users  | 2  | 200      | missing-login |
  | admin     | users  | 2  | 302      | none |

  Scenario Outline: Delete GET
    Given a <role> user
     When opens the delete page for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Delete GET
  | role      | modul | id | response |
  | anonymous | user  | 2  | 403      |
  | admin     | user  | 2  | 200      |

  Scenario Outline: Delete POST
    Given a <role> user
     When opens the delete page for item <id> of modul <modul>
     When confirms deletion for item <id> of modul <modul>
     Then the user should get a <response> http response

  Examples: Delete POST
  | role      | modul | id | response |
  | admin     | user  | 2  | 302      |
