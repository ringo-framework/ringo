from datetime import datetime
from mock import Mock
import pkg_resources
from ringo.tests import BaseUnitTest


class HelpersTests(BaseUnitTest):

    def test_get_saved_searches_unauthorized(self):
        from ringo.lib.helpers import get_saved_searches
        self.request.user = None
        result = get_saved_searches(self.request, "test")
        self.assertEquals(result, {})


class HelpersAuthTests(BaseUnitTest):

    def test_serialize_datetime(self):
        from ringo.lib.helpers import serialize
        dt = datetime(1977, 3, 12, 0, 0, 0)
        result = serialize(dt)
        self.assertEquals(result, "1977-03-12 00:00:00")
        self.assertEquals(type(result), str)

    def test_serialize_int(self):
        from ringo.lib.helpers import serialize
        result = serialize(23)
        self.assertEquals(result, "23")
        self.assertEquals(type(result), unicode)

    def test_serialize_list(self):
        from ringo.lib.helpers import serialize
        result = serialize(["foo", "bar", "baz"])
        self.assertEquals(result, "['foo', 'bar', 'baz']")
        self.assertEquals(type(result), unicode)

    def test_import_ok(self):
        from ringo.lib.helpers import dynamic_import
        result = dynamic_import('ringo.model.base.BaseItem')
        self.assertEquals(repr(result), "<class 'ringo.model.base.BaseItem'>")

    def test_import_fails(self):
        from ringo.lib.helpers import dynamic_import
        with self.assertRaises(AttributeError):
            dynamic_import('ringo.model.base.IamNotHere')

    def test_get_app_name(self):
        from ringo.lib.helpers import get_app_name
        result = get_app_name()
        self.assertEquals(result, "ringo")

    def test_get_app_title(self):
        from ringo.lib.helpers import get_app_title
        result = get_app_title()
        self.assertEquals(result, "Ringo")

    def test_get_action_url_read(self):
        from ringo.lib.helpers import get_action_url
        self.config.add_route('supertable-read', '/supertables/read/{id}')
        item = Mock()
        item.id = 1
        item.__tablename__ = "supertable"
        result = get_action_url(self.request, item, 'read')
        self.assertEquals(result, "/supertables/read/1")

    def test_get_action_url_list(self):
        from ringo.lib.helpers import get_action_url
        from ringo.lib.helpers import import_model
        user = import_model('ringo.model.user.User')
        self.config.add_route('users-list', '/users/list')
        result = get_action_url(self.request, user, 'list')
        self.assertEquals(result, "/users/list")

    def test_get_path_to(self):
        from ringo.lib.helpers import get_path_to
        location = pkg_resources.get_distribution("ringo").location
        result = get_path_to("this/is/my/location")
        self.assertEquals(result, location + "/ringo/this/is/my/location")

    def test_get_app_location(self):
        from ringo.lib.helpers import get_app_location
        location = pkg_resources.get_distribution("ringo").location
        result = get_app_location()
        self.assertEquals(result, location)

    def test_get_path_to_form_config(self):
        from ringo.lib.helpers import get_path_to_form_config
        location = pkg_resources.get_distribution("ringo").location
        result = get_path_to_form_config("foo.xml")
        self.assertEquals(result, location + "/ringo/views/forms/foo.xml")

    def test_get_path_to_table_config(self):
        from ringo.lib.helpers import get_path_to_overview_config
        location = pkg_resources.get_distribution("ringo").location
        result = get_path_to_overview_config("foo.json")
        self.assertEquals(result, location + "/ringo/views/tables/foo.json")

    def test_get_ringo_version(self):
        from ringo.lib.helpers import get_ringo_version
        result = get_ringo_version()
        self.assertTrue(isinstance(result, basestring))

    def test_import_model(self):
        from ringo.lib.helpers import import_model
        result = import_model('ringo.model.user.User')
        self.assertEquals(result.__tablename__, "users")

    def test_get_saved_searches_authorized(self):
        from ringo.lib.helpers import get_saved_searches
        result = get_saved_searches(self.request, "foo")
        self.assertEquals(result, "bar")

    def test_get_modules(self):
        from ringo.lib.helpers import get_modules
        result = get_modules(self.request, 'admin-menu')
        self.assertEquals(len(result), 10)

    def test_get_formbar_css(self):
        from ringo.lib.helpers import get_formbar_css
        result = get_formbar_css()
        self.assertTrue(isinstance(result, list))

    def test_get_formbar_js(self):
        from ringo.lib.helpers import get_formbar_js
        result = get_formbar_js()
        self.assertTrue(isinstance(result, list))

    def test_prettify_nondate(self):
        from ringo.lib.helpers import prettify
        result = prettify(self.request, "Test")
        self.assertEquals(result, "Test")

    def test_prettify_date(self):
        from ringo.lib.helpers import prettify
        result = prettify(self.request, datetime(1977, 3, 12, 0, 0, 0))
        # The result of the prettify function for datetimes is not
        # constant and seems to depend on some system settings.
        # So test all known variants
        check1 = (result == u"3/12/77 12:00 AM")
        check2 = (result == u"3/12/77, 12:00 AM")
        ok = check1 or check2
        self.assertTrue(ok)

    def test_format_datetime(self):
        from ringo.lib.helpers import format_datetime
        result = format_datetime(datetime(1977, 3, 12, 0, 0, 0))
        self.assertEquals(result, u"1977-03-12 00:00")

    def test_get_week(self):
        from ringo.lib.helpers import get_week
        result = get_week(datetime(1977, 3, 12, 0, 0, 0))
        start = datetime(1977, 3, 7, 0, 0)
        end = datetime(1977, 3, 13, 23, 59, 59)
        self.assertEquals(result, (start, end))

    def test_format_positiv_timedelta(self):
        from ringo.lib.helpers import format_timedelta
        start = datetime(1977, 3, 7, 0, 0)
        end = datetime(1977, 3, 7, 1, 0)
        result = format_timedelta(end - start)
        self.assertEquals(result, "01:00:00")

    def test_format_negative_timedelta(self):
        from ringo.lib.helpers import format_timedelta
        start = datetime(1977, 3, 7, 0, 0)
        end = datetime(1977, 3, 7, 1, 0)
        result = format_timedelta(start - end)
        self.assertEquals(result, "-01:00:00")
