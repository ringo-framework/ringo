from ringo.tests import BaseUnitTest


class ModulTests(BaseUnitTest):

    def _load_item(self):
        from ringo.model.modul import ModulItem
        factory = ModulItem.get_item_factory()
        return factory.load(1)

    def test_get_label(self):
        item = self._load_item()
        result = item.get_label()
        self.assertEqual(result, "Modul")

    def test_get_label_plural(self):
        item = self._load_item()
        result = item.get_label(plural=True)
        self.assertEqual(result, "Modules")
