import hashlib
import unittest
import transaction

from pyramid import testing

from ringo.model import DBSession, Base
from ringo.model.modul import (
    init_model as init_modul_model,
)
from ringo.model.user import (
    init_model as init_user_model
)


class TestInit(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        with transaction.manager:
            init_modul_model(DBSession)
            init_user_model(DBSession)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()
