from ringo.tests import BaseUnitTest

from pyramid import testing

class StaticViewTests(BaseUnitTest):
    def setUp(self):
        """ This sets up the application registry with the
        registrations your application declares in its ``includeme``
        function.
        """
        super(BaseUnitTest, self).setUp()
        self.config = testing.setUp(self.registry)

    def tearDown(self):
        """ Clear out the application registry """
        testing.tearDown()

    def test_home_unauthenticated_view(self):
        from ringo.views.home import index_view
        request = testing.DummyRequest()
        user = None
        request.user = user
        result = index_view(request)
        self.assertEqual(len(result), 0)

    def test_home_authenticated_view(self):
        from ringo.views.home import index_view
        result = index_view(self.get_request(user="xxx"))
        self.assertEqual(len(result), 3)
        self.assertTrue("todos" in result.keys())
        self.assertTrue("reminders" in result.keys())
        self.assertTrue("news" in result.keys())

    def test_about_view(self):
        from ringo.views.home import about_view
        request = testing.DummyRequest()
        result = about_view(request)
        self.assertEqual(result['app_title'], 'Ringo')

    def test_contact_view(self):
        from ringo.views.home import contact_view
        request = testing.DummyRequest()
        result = contact_view(request)
        self.assertEqual(len(result), 0)

    def test_version_view(self):
        from ringo.views.home import version_view
        request = testing.DummyRequest()
        result = version_view(request)
        self.assertEqual(len(result), 7)
        self.assertEqual(result['app_title'], 'Ringo')
        self.assertEqual(result['app_name'], "ringo")
