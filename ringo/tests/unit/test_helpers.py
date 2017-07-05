import pytest

pytestmark = pytest.mark.usefixtures("config")


def test_serialize_datetime():
    from ringo.lib.helpers import serialize
    from datetime import datetime
    dt = datetime(1977, 3, 12, 0, 0, 0)
    result = serialize(dt)
    assert result == "1977-03-12 00:00:00"
    assert type(result) == str


def test_serialize_int():
    from ringo.lib.helpers import serialize
    result = serialize(23)
    assert result == "23"
    assert type(result) == unicode


def test_serialize_list():
    from ringo.lib.helpers import serialize
    result = serialize(["foo", "bar", "baz"])
    assert result == "['foo', 'bar', 'baz']"
    assert type(result) == unicode


def test_import_ok():
    from ringo.lib.helpers import dynamic_import
    result = dynamic_import('ringo.model.base.BaseItem')
    assert repr(result) == "<class 'ringo.model.base.BaseItem'>"


def test_import_fails():
    from ringo.lib.helpers import dynamic_import
    with pytest.raises(AttributeError):
        dynamic_import('ringo.model.base.IamNotHere')


def test_get_app_name():
    from ringo.lib.helpers import get_app_name
    result = get_app_name()
    assert result == "ringo"


def test_get_app_title():
    from ringo.lib.helpers import get_app_title
    result = get_app_title()
    assert result == "Ringo"


def test_get_action_url_read(apprequest, config):
    from ringo.lib.helpers import get_action_url
    from mock import Mock
    config.add_route('supertable-read', '/supertables/read/{id}')
    item = Mock()
    item.id = 1
    item.__tablename__ = "supertable"
    result = get_action_url(apprequest, item, 'read')
    assert result == "/supertables/read/1"


def test_get_action_url_list(apprequest, config):
    from ringo.lib.helpers import get_action_url
    from ringo.lib.helpers import import_model
    user = import_model('ringo.model.user.User')
    config.add_route('users-list', '/users/list')
    result = get_action_url(apprequest, user, 'list')
    assert result == "/users/list"


def test_get_path_to():
    import pkg_resources
    from ringo.lib.helpers import get_path_to
    location = pkg_resources.get_distribution("ringo").location
    result = get_path_to("this/is/my/location")
    assert result == location + "/ringo/this/is/my/location"


def test_get_app_location():
    import pkg_resources
    from ringo.lib.helpers import get_app_location
    location = pkg_resources.get_distribution("ringo").location
    result = get_app_location()
    assert result == location


def test_get_path_to_form_config():
    import pkg_resources
    from ringo.lib.form import get_path_to_form_config
    location = pkg_resources.get_distribution("ringo").location
    result = get_path_to_form_config("foo.xml")
    assert result == location + "/ringo/views/forms/foo.xml"


def test_get_path_to_table_config():
    import pkg_resources
    from ringo.lib.table import get_path_to_overview_config
    location = pkg_resources.get_distribution("ringo").location
    result = get_path_to_overview_config("foo.json")
    assert result == location + "/ringo/views/tables/foo.json"


def test_get_ringo_version():
    from ringo.lib.helpers import get_ringo_version
    result = get_ringo_version()
    assert isinstance(result, basestring)


def test_import_model():
    from ringo.lib.helpers import import_model
    result = import_model('ringo.model.user.User')
    assert result.__tablename__ == "users"


def test_get_saved_searches_authorized(apprequest):
    from ringo.lib.helpers import get_saved_searches
    result = get_saved_searches(apprequest, "foo")
    assert result == "bar"


def test_get_modules(apprequest):
    from ringo.lib.helpers import get_modules
    result = get_modules(apprequest, 'admin-menu')
    # Will result 0 here as the we must trigger a "real" request to
    # the application before as the modules are precached than.
    assert len(result) == 0


def test_get_formbar_css():
    from ringo.lib.form import get_formbar_css
    result = get_formbar_css()
    assert isinstance(result, list)


def test_get_formbar_js():
    from ringo.lib.form import get_formbar_js
    result = get_formbar_js()
    assert isinstance(result, list)


def test_prettify_nondate(apprequest):
    from ringo.lib.helpers import prettify
    result = prettify(apprequest, "Test")
    assert result == "Test"


def test_prettify_date(apprequest):
    from ringo.lib.helpers import prettify
    from datetime import datetime
    from dateutil import tz
    dt = datetime(1977, 3, 12, 0, 0, 0, )
    dt = dt.replace(tzinfo=tz.tzlocal())
    result = prettify(apprequest, dt)
    assert result == u"1977-03-12 00:00"


def test_format_datetime():
    from datetime import datetime
    from ringo.lib.helpers import format_datetime
    result = format_datetime(datetime(1977, 3, 12, 0, 0, 0))
    assert result == u"1977-03-12 00:00"


def test_get_week():
    from datetime import datetime
    from ringo.lib.helpers import get_week
    result = get_week(datetime(1977, 3, 12, 0, 0, 0))
    start = datetime(1977, 3, 7, 0, 0)
    end = datetime(1977, 3, 13, 23, 59, 59)
    assert result == (start, end)


def test_format_positiv_timedelta():
    from datetime import datetime
    from ringo.lib.helpers import format_timedelta
    start = datetime(1977, 3, 7, 0, 0)
    end = datetime(1977, 3, 7, 1, 0)
    result = format_timedelta(end - start)
    assert result == "01:00:00"


def test_format_negative_timedelta():
    from datetime import datetime
    from ringo.lib.helpers import format_timedelta
    start = datetime(1977, 3, 7, 0, 0)
    end = datetime(1977, 3, 7, 1, 0)
    result = format_timedelta(start - end)
    assert result == "-01:00:00"


def test_get_saved_searches_unauthorized(apprequest):
    from ringo.lib.helpers import get_saved_searches
    apprequest.user = None
    result = get_saved_searches(apprequest, "test")
    assert result == {}
