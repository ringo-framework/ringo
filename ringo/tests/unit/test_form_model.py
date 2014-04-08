from ringo.tests import BaseUnitTest


class FormTests(BaseUnitTest):

    def test_create_form(self):
        """Testfunction to trigger execution of Statemachine code"""
        from ringo.model.form import Form
        factory = Form.get_item_factory()
        item = factory.create(user=None)
        result = item.review_state
        self.assertEqual(result._id, 1)
