import pytest
import json

pytestmark = pytest.mark.usefixtures("config")

@pytest.fixture()
def expected_item():
    return json.loads(
        """
        {"default_gid": null,
        "uuid": "",
        "activated": true,
        "gid": 1,
        "last_login": "",
        "sid": 1,
        "login": "admin",
        "password": "xxx",
        "id": 1,
        "activation_token": "",
        "uid": 1}
        """
    )

@pytest.fixture()
def import_item(expected_item):
    import_item = expected_item
    import_item["login"] = "test"
    del import_item["uuid"]
    return import_item

@pytest.fixture()
def import_byid_item(import_item):
    del import_item["id"]
    return import_item

@pytest.fixture()
def update_import_byuuid_item(import_item):
    from ringo.lib.sql import DBSession
    from ringo.model.user import User

    import_item["uuid"] = DBSession.query(
        User.uuid).filter(User.id == import_item["id"]).scalar()
    return import_item


def test_item_export(expected_item):
    from ringo.model.base import BaseFactory
    from ringo.model.user import User
    from ringo.lib.imexport import JSONExporter

    user = BaseFactory(User).load(1)
    export = json.loads(JSONExporter(User, serialized=False).perform(user))

    assert sorted(export.keys()) == sorted(expected_item.keys())

    for key in [key for key in expected_item.keys()
                if key not in ["uuid", "last_login", "password"]]:
        assert export[key] == expected_item[key]


class TestJSONImport(object):

    def test_import(self, import_item):
        from ringo.model.user import User
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession
        from ringo.model.base import BaseFactory

        imported_items = JSONImporter(User).perform(json.dumps(import_item))
        DBSession.flush()

        assert len(imported_items) == 1
        assert imported_items[0][1] == "CREATE"
        assert (imported_items[0][0]
                is BaseFactory(User).load(imported_items[0][0].id))


    def test_update_import(self, update_import_byuuid_item):
        from ringo.model.user import User
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession
        from ringo.model.base import BaseFactory

        imported_items = JSONImporter(User).perform(
            json.dumps(update_import_byuuid_item))
        DBSession.flush()

        assert len(imported_items) == 1
        assert imported_items[0][1] == "UPDATE"
        assert (BaseFactory(User).load(update_import_byuuid_item["uuid"],
                                       field="uuid").login
                == update_import_byuuid_item["login"])


    def test_import_byid(self, import_byid_item):
        from ringo.model.user import User
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession

        imported_items = JSONImporter(User).perform(json.dumps(import_byid_item),
                                                    load_key = "id")
        DBSession.flush()

        assert len(imported_items) == 1
        assert imported_items[0][1] == "CREATE"
        assert imported_items[0][0].login == import_byid_item["login"]


    def test_update_import_byid(self, import_item):
        from ringo.model.user import User
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession
        from ringo.model.base import BaseFactory

        imported_items = JSONImporter(User).perform(
            json.dumps(import_item),
            load_key = "id")
        DBSession.flush()

        assert len(imported_items) == 1
        assert imported_items[0][1] == "UPDATE"
        assert (BaseFactory(User).load(import_item["id"]).login
                == import_item["login"])


    def test_import_byname(self, import_item):
        from ringo.model.user import User
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession

        imported_items = JSONImporter(User).perform(json.dumps(import_item),
                                                    load_key = "login")
        DBSession.flush()

        assert len(imported_items) == 1
        assert imported_items[0][1] == "CREATE"
        assert imported_items[0][0].login == import_item["login"]
