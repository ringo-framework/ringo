Feature: Check the modul
  Will check if the basic CRUD oprations for the modul are working

  Scenario Outline: Create GET
    Given a <role> user
     When opens the create page of modul <modul>
     Then the user should get a <response> http respone

  Examples: User
  | role      | modul | response |
  | anonymous | user  | 403      |
  | admin     | user  | 200      |

  Examples: Usergroup
  | role      | modul     | response |
  | anonymous | usergroup | 403      |
  | admin     | usergroup | 200      |

  Examples: Rolemodul
  | role      | modul | response |
  | anonymous | role  | 403      |
  | admin     | role  | 200      |

  Examples: Profil
  | role      | modul  | response |
  | anonymous | profil | 404      |
  | admin     | profil | 404      |

  Examples: Modul
  | role      | modul  | response |
  | anonymous | modul  | 404      |
  | admin     | modul  | 404      |

  Examples: Appointment
  | role      | modul        | response |
  | anonymous | appointment  | 403      |
  | admin     | appointment  | 200      |

  Examples: File
  | role      | modul | response |
  | anonymous | file  | 403      |
  | admin     | file  | 200      |

  Examples: News
  | role      | modul | response |
  | anonymous | news  | 403      |
  | admin     | news  | 200      |

  Scenario Outline: Read GET
    Given a <role> user
     When opens the read page for item <id> of modul <modul>
     Then the user should get a <response> http respone

  Examples: User
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |

  Examples: Usergroup
  | role      | modul     | id | response |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |

  Examples: Rolemodul
  | role      | modul | id | response |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |

  Examples: Profil
  | role      | modul  | id | response |
  | anonymous | profil | 1  | 403      |
  | admin     | profil | 1  | 200      |

  Examples: Modul
  | role      | modul  | id | response |
  | anonymous | modul  | 1  | 403      |
  | admin     | modul  | 1  | 200      |

  Examples: Appointment
  | role      | modul        | id | response |
  | anonymous | appointment  | 1  | 403      |
  | admin     | appointment  | 1  | 400      |

  Examples: File
  | role      | modul | id | response |
  | anonymous | file  | 1  | 403      |
  | admin     | file  | 1  | 400      |

  Examples: File
  | role      | modul | id | response |
  | anonymous | news  | 1  | 403      |
  | admin     | news  | 1  | 400      |



  Scenario Outline: Edit GET
    Given a <role> user
     When opens the edit page for item <id> of modul <modul>
     Then the user should get a <response> http respone

  Examples: User
  | role      | modul | id | response |
  | anonymous | user  | 1  | 403      |
  | admin     | user  | 1  | 200      |

  Examples: Usergroup
  | role      | modul     | id | response |
  | anonymous | usergroup | 1  | 403      |
  | admin     | usergroup | 1  | 200      |

  Examples: Rolemodul
  | role      | modul | id | response |
  | anonymous | role  | 1  | 403      |
  | admin     | role  | 1  | 200      |

  Examples: Profil
  | role      | modul  | id | response |
  | anonymous | profil | 1  | 403      |
  | admin     | profil | 1  | 200      |

  Examples: Modul
  | role      | modul  | id | response |
  | anonymous | modul  | 1  | 403      |
  | admin     | modul  | 1  | 200      |

  Examples: Appointment
  | role      | modul        | id | response |
  | anonymous | appointment  | 1  | 403      |
  | admin     | appointment  | 1  | 400      |

  Examples: File
  | role      | modul | id | response |
  | anonymous | file  | 1  | 403      |
  | admin     | file  | 1  | 400      |

  Examples: File
  | role      | modul | id | response |
  | anonymous | news  | 1  | 403      |
  | admin     | news  | 1  | 400      |
