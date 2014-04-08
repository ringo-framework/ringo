import pyramid
from ringo.tests import BaseUnitTest


class ViewHelpersTests(BaseUnitTest):

    def setUp(self):
        super(ViewHelpersTests, self).setUp()
        # TODO: Load modul item and put it into the context of the
        # request (ti) <2014-04-07 20:32>
        from ringo.model.modul import ModulItem
        item = self.request.db.query(ModulItem).filter(ModulItem.id == 1).one()
        self.request.context.item = item
        self.request.matchdict = {'id': 1}
        self.request.session['modules.1.form.page'] = 2

    def test_get_context(self):
        from ringo.views.base import _get_item_from_context
        result = _get_item_from_context(self.request)
        self.assertEqual(result.name, 'modules')

    def test_get_context_fail(self):
        from ringo.views.base import _get_item_from_context
        self.request.context.item = None
        with self.assertRaises(pyramid.httpexceptions.HTTPBadRequest):
            _get_item_from_context(self.request)

    def test_get_current_formpage(self):
        from ringo.model.modul import ModulItem
        from ringo.views.base import get_current_form_page
        result = get_current_form_page(ModulItem, self.request)
        self.assertEqual(result, 2)

    def test_get_current_formpage_default(self):
        from ringo.model.modul import ModulItem
        from ringo.views.base import get_current_form_page
        self.request.session = {}
        result = get_current_form_page(ModulItem, self.request)
        self.assertEqual(result, 1)

    def test_get_ownership_form(self):
        from ringo.views.base import get_ownership_form
        from ringo.views.base import _get_item_from_context
        item = _get_item_from_context(self.request)
        result = get_ownership_form(item, self.request)
        self.assertEqual(len(result.fields.keys()), 2)
        self.assertEqual(result._item, item)

    def test_get_ownership_form_readonly(self):
        from ringo.views.base import get_ownership_form
        from ringo.views.base import _get_item_from_context
        item = _get_item_from_context(self.request)
        result = get_ownership_form(item, self.request, True)
        self.assertEqual(len(result.fields.keys()), 2)
        self.assertEqual(result._item, item)

    def test_get_ownership_form_owned(self):
        from ringo.model.user import Profile
        from ringo.views.base import get_ownership_form
        item = self.request.db.query(Profile).filter(Profile.id == 1).one()
        result = get_ownership_form(item, self.request)
        self.assertEqual(len(result.fields.keys()), 2)
        self.assertEqual(result._item, item)

    def test_get_logbook_form(self):
        from ringo.views.base import get_logbook_form
        from ringo.views.base import _get_item_from_context
        item = _get_item_from_context(self.request)
        result = get_logbook_form(item, self.request)
        self.assertEqual(len(result.fields.keys()), 1)
        self.assertEqual(result._item, item)

    def test_get_logbook_form_readonly(self):
        from ringo.views.base import get_logbook_form
        from ringo.views.base import _get_item_from_context
        item = _get_item_from_context(self.request)
        result = get_logbook_form(item, self.request, True)
        self.assertEqual(len(result.fields.keys()), 1)
        self.assertEqual(result._item, item)

    def test_get_logbook_form_owned(self):
        from ringo.model.user import Profile
        from ringo.views.base import get_logbook_form
        item = self.request.db.query(Profile).filter(Profile.id == 1).one()
        result = get_logbook_form(item, self.request)
        self.assertEqual(len(result.fields.keys()), 1)
        self.assertEqual(result._item, item)

#class CRUDViewTests(BaseUnitTest):
#
#    def setUp(self):
#        super(CRUDViewTests, self).setUp()
#        # TODO: Load modul item and put it into the context of the
#        # request (ti) <2014-04-07 20:32>
#        self.request.context = Mock()
#
#    def test_read(self):
#        from ringo.model.modul import ModulItem
#        from ringo.views.base import read_
#        result = read_(ModulItem, self.request)
#        self.assertEqual(len(result), 3)
