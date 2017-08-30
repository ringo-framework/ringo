import pytest
import json
import copy
import uuid

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


@pytest.fixture()
def nested_import_item(import_item):
    # many-to-one relation
    import_item["usergroup"] = json.loads(
        """
        {
        "uid": 1,
        "gid": 1,
        "name": "testgroup",
        "description": "test"
        }
        """
    )

    # one-to-one relation
    import_item["profile"] = json.loads(
        """
        [{
        "uid": 1,
        "gid": 1,
        "first_name": "Test"
        }]
        """
    )

    # many-to-many relation
    import_item["roles"] = json.loads(
        """
        [{
        "label": "Test-role",
        "name": "testrole",
        "admin": false,
        "gid": 1,
        "uid": 1
        },
        {
        "label": "Another Test-role",
        "name": "testrole2",
        "admin": false,
        "gid": 1,
        "uid": 1
        }]
        """
    )

    return import_item


@pytest.fixture()
def nested_import_items(nested_import_item):
    from ringo.lib.sql import DBSession
    from ringo.lib.imexport import JSONExporter
    from ringo.model.user import Usergroup, Role

    import_items = [nested_import_item, copy.deepcopy(nested_import_item)]
    import_items[1]["login"] = "test2"

    # update-import relations of second item
    import_items[1]["usergroup"] = json.loads(
        JSONExporter(Usergroup, serialized=False).perform(
            DBSession.query(Usergroup).filter(Usergroup.name == 'users').one()))
    import_items[1]["roles"] = json.loads(
        JSONExporter(Role, serialized=False).perform(
            DBSession.query(Role).all()))

    # Identifiable related object can appear multiple times
    import_items[0]["roles"][0]["uuid"] = str(uuid.uuid4())
    import_items[1]["roles"].append(import_items[0]["roles"][0])

    return import_items


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


    def test_recursive_import(self, nested_import_item):
        from ringo.model.user import User
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession

        imported_items = JSONImporter(User).perform(
            json.dumps(nested_import_item))
        DBSession.flush()

        assert len(imported_items) == 1
        assert imported_items[0][1] == "CREATE"
        assert (imported_items[0][0].usergroup.name
                == nested_import_item["usergroup"]["name"])
        assert (imported_items[0][0].profile[0].first_name
                == nested_import_item["profile"][0]["first_name"])
        assert (len(imported_items[0][0].roles)
                == len(nested_import_item["roles"]))
        assert (imported_items[0][0].roles[0].name
                == nested_import_item["roles"][0]["name"])


    def test_recursive_import_multiple(self, nested_import_items):
        from ringo.model.user import User, Usergroup, Role
        from ringo.lib.imexport import JSONImporter
        from ringo.lib.sql import DBSession

        group_count = DBSession.query(Usergroup).count()
        role_count = DBSession.query(Role).count()
        imported_items = JSONImporter(User).perform(
            json.dumps(nested_import_items))
        DBSession.flush()

        assert len(imported_items) == 2
        assert all(i[1] == "CREATE" for i in imported_items)
        # plus automatically created and one imported (not updated) groups:
        assert (DBSession.query(Usergroup).count()
                == group_count + len(nested_import_items) + 1)
        # plus imported (not updated) groups:
        assert (DBSession.query(Role).count()
                == role_count + len(nested_import_items[0]["roles"]))
