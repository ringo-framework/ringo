from ringo.tests import BaseUnitTest


class CRUDViewTests(BaseUnitTest):

    def setUp(self):
        super(CRUDViewTests, self).setUp()
        # TODO: Load modul item and put it into the context of the
        # request (ti) <2014-04-07 20:32>

    def test_read(self):
        from ringo.model.modul import ModulItem
        from ringo.views.base import read_
        result = read_(ModulItem, self.request)
        self.assertEqual(len(result), 3)
