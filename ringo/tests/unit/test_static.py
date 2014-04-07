from ringo.tests import BaseUnitTest


class StaticAuthViewTests(BaseUnitTest):

    def test_home_authenticated_view(self):
        from ringo.views.home import index_view
        result = index_view(self.request)
        self.assertEqual(len(result), 3)
        self.assertTrue("todos" in result.keys())
        self.assertTrue("reminders" in result.keys())
        self.assertTrue("news" in result.keys())

    def test_about_view(self):
        from ringo.views.home import about_view
        result = about_view(self.request)
        self.assertEqual(result['app_title'], 'Ringo')

    def test_contact_view(self):
        from ringo.views.home import contact_view
        result = contact_view(self.request)
        self.assertEqual(len(result), 0)

    def test_version_view(self):
        from ringo.views.home import version_view
        result = version_view(self.request)
        self.assertEqual(len(result), 7)
        self.assertEqual(result['app_title'], 'Ringo')
        self.assertEqual(result['app_name'], "ringo")


class StaticViewTests(BaseUnitTest):

    def test_home_unauthenticated_view(self):
        from ringo.views.home import index_view
        self.request.user = None
        result = index_view(self.request)
        self.assertEqual(len(result), 0)
