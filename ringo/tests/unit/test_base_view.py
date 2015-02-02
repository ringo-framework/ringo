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
        from ringo.views.helpers import get_item_from_request
        result = get_item_from_request(self.request)
        self.assertEqual(result.name, 'modules')

    def test_get_context_fail(self):
        from ringo.views.helpers import get_item_from_request
        self.request.context.item = None
        with self.assertRaises(pyramid.httpexceptions.HTTPBadRequest):
            get_item_from_request(self.request)

    def test_get_current_formpage(self):
        from ringo.model.modul import ModulItem
        from ringo.views.helpers import get_current_form_page
        result = get_current_form_page(ModulItem, self.request)
        self.assertEqual(result, 2)

    def test_get_current_formpage_default(self):
        from ringo.model.modul import ModulItem
        from ringo.views.helpers import get_current_form_page
        self.request.session = {}
        result = get_current_form_page(ModulItem, self.request)
        self.assertEqual(result, 1)

    def test_get_ownership_form(self):
        from ringo.views.helpers import (
            get_ownership_form,
            get_item_from_request
        )
        item = get_item_from_request(self.request)
        result = get_ownership_form(self.request)
        self.assertEqual(len(result.fields.keys()), 5)
        self.assertEqual(result._item, item)

    def test_get_ownership_form_readonly(self):
        from ringo.views.helpers import (
            get_ownership_form,
            get_item_from_request
        )
        item = get_item_from_request(self.request)
        result = get_ownership_form(self.request, True)
        self.assertEqual(len(result.fields.keys()), 2)
        self.assertEqual(result._item, item)
