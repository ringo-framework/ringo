Feature: Check the modul
  Will check if the basic CRUD oprations for the modul are working

  Scenario Outline: Create GET
    Given a <role> user
     When opens the create page of modul <modul>
     Then the user should get a <response> http respone

  Examples: Usermodul
  | role      | modul | response |
  | anonymous | user  | 403      |
  | admin     | user  | 200      |

  Examples: Rolemodul
  | role      | modul | response |
  | anonymous | role  | 403      |
  | admin     | role  | 200      |

  Scenario Outline: Read GET
    Given a <role> user
     When opens the read page for item <id> of modul <modul>
     Then the user should get a <response> http respone

  Examples: Usermodul
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |

  Examples: Rolemodul
  | role      | modul | id | response |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |


  Scenario Outline: Edit GET
    Given a <role> user
     When opens the edit page for item <id> of modul <modul>
     Then the user should get a <response> http respone

  Examples: Usermodul
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |

  Examples: Rolemodul
  | role      | modul | id | response |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |

