from ringo.tests import BaseUnitTest

class GlobalTests(BaseUnitTest):

    def test_clear_cache(self):
        from ringo.model.base import clear_cache
        clear_cache()

class BaseItemTests(BaseUnitTest):

    def _load_item(self):
        from ringo.model.modul import ModulItem
        factory = ModulItem.get_item_factory()
        return factory.load(1)

    def test_load_item(self):
        item = self._load_item()
        result = item.render()
        self.assertEqual(result, "modules")

    def test_get_item(self):
        item = self._load_item()
        result = item['name']
        self.assertEqual(result, "modules")

    def test_unicode(self):
        item = self._load_item()
        result = unicode(item)
        self.assertEqual(result, u"modules")

    def test_json(self):
        item = self._load_item()
        result = item.__json__(self.request)
        self.assertEqual(len(result), len('[{"str_repr": "%s|name", "description": "", "name": "modules", "label": "Modul", "gid": "", "id": "1", "label_plural": "Modules", "display": "admin-menu", "clazzpath": "ringo.model.modul.ModulItem", "uuid": ""}]'))

    def test_get_form_config(self):
        from ringo.model.modul import ModulItem
        result = ModulItem.get_form_config('create')
        self.assertEqual(result.id, 'create')

    def test_get_action_routename(self):
        from ringo.model.modul import ModulItem
        result = ModulItem.get_action_routename('create')
        self.assertEqual(result, 'modules-create')

    def test_get_action_routename_prefixed(self):
        from ringo.model.modul import ModulItem
        result = ModulItem.get_action_routename('create', 'rest')
        self.assertEqual(result, 'rest-modules-create')

    def test_get_changes(self):
        item = self._load_item()
        # FIXME: Can not change the value temporarily. Will break other
        # testcases.(ti) <2014-04-08 15:54>
        #old = item.label
        #item.label= "xxx"
        result = item.get_changes()
        #self.assertEqual(result, {'label': ([u'Modul'], ['xxx'])})
        self.assertEqual(result, {})
        #item.label= old

    def test_get_values(self):
        item = self._load_item()
        result = item.get_values()
        self.assertEqual(result['name'], 'modules')

    def test_get_serialized_values(self):
        item = self._load_item()
        result = item.get_values(serialized=True)
        self.assertEqual(result['name'], 'modules')

    def test_save(self):
        item = self._load_item()
        values = item.get_values()
        item.save(values)
        self.assertEqual(item['name'], 'modules')

    def test_get_item_factory(self):
        from ringo.model.modul import ModulItem
        from ringo.model.base import BaseFactory
        result = ModulItem.get_item_factory()
        self.assertEqual(result._clazz, ModulItem)
        self.assertTrue(isinstance(result, BaseFactory))

    def test_get_item_list(self):
        from ringo.model.modul import ModulItem
        from ringo.model.base import BaseList
        result = ModulItem.get_item_list(self.request, user=None)
        self.assertTrue(isinstance(result, BaseList))

    def test_get_item_actions(self):
        from ringo.model.modul import ModulItem
        from ringo.model.modul import ActionItem
        result = ModulItem.get_item_actions()
        self.assertTrue(isinstance(result, list))
        if len(result) > 0:
            self.assertTrue(isinstance(result[0], ActionItem))
