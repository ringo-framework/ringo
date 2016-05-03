#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import (
    login, logout, transaction_begin, transaction_rollback,
    search_data, get_data
)

def create_user(app, login):
    """Will create a new user with the given loginname.
    :app: TODO
    :login: Loginname of the user
    :returns: Result of post request
    """
    values = {"login": login,
              "password": "123123123qwe",
              "_retype_password": "123123123qwe",
              "_first_name": u"Först", "_last_name": "Last",
              "_email": "%s@example.com" % login}
    return app.post("/users/create", params=values, status=302)


class TestList:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/users/list")


class TestRead:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/users/read/1")


class TestCreate:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/users/create")

    def test_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        create_user(app, "test")
        transaction_rollback(app)

    def test_POST_password_tooshort(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "test",
                  "password": "123",
                  "_retype_password": "123",
                  "_first_name": u"Först", "_last_name": "Last",
                  "_email": "email@example.com"}
        app.post("/users/create", params=values, status=200)
        transaction_rollback(app)

    def test_POST_password_missmatch(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "test",
                  "password": "123123123ewq",
                  "_retype_password": "123123123qwe",
                  "_first_name": u"Först", "_last_name": "Last",
                  "_email": "email@example.com"}
        app.post("/users/create", params=values, status=200)
        transaction_rollback(app)

    def test_POST_existing_user(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "admin",
                  "password": "123123123qwe",
                  "_retype_password": "123123123qwe",
                  "_first_name": u"Först", "_last_name": "Last",
                  "_email": "email@example.com"}
        app.post("/users/create", params=values, status=200)
        transaction_rollback(app)


class TestUpdate:

    def test_update(self, app):
        login(app, "admin", "secret")
        app.get("/users/update/1")

    def test_update_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "admintest"}
        app.post("/users/update/1", params=values, status=302)
        transaction_rollback(app)


    def test_update_POST_missing_login(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": ""}
        app.post("/users/update/1", params=values, status=200)
        transaction_rollback(app)


class TestDelete:

    def test_delete(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "test",
                  "password": "123123123qwe",
                  "_retype_password": "123123123qwe",
                  "_first_name": u"Först", "_last_name": "Last",
                  "_email": "email@example.com"}
        result = app.post("/users/create", params=values, status=302)
        id = result.headers["Location"].split("/")[-1]
        app.get("/users/delete/%s" % id)
        app.get("/users/list")
        transaction_rollback(app)

    def test_delete_POST_confirm_yes(self, app):
        """Test if a created user can be deleted. The transaction is not
        actived here. As this seems to cause errors"""
        login(app, "admin", "secret")
        values = {"login": "test",
                  "password": "123123123qwe",
                  "_retype_password": "123123123qwe",
                  "_first_name": u"Först", "_last_name": "Last",
                  "_email": "email@example.com"}
        result = app.post("/users/create", params=values, status=302)
        id = result.headers["Location"].split("/")[-1]
        values = {"confirmed": 1}
        app.post("/users/delete/%s" % id, params=values, status=302)

    @pytest.mark.xfail
    def test_delete_POST_admin_confirm_yes(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/users/delete/1", params=values, status=200)

class TestChangeOwnPassword:

    def test_change(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "admin", "oldpassword": "secret",
                  "password": "123123123qwe",
                  "_retype_password": "123123123qwe"}
        result = app.post("/users/changepassword/1", params=values, status=302)
        transaction_rollback(app)

    def test_change_wrong_old_pw(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "admin", "oldpassword": "secretwrong",
                  "password": "123123123qwe",
                  "_retype_password": "123123123qwe"}
        result = app.post("/users/changepassword/1", params=values, status=200)
        transaction_rollback(app)

    def test_change_password_missmatch(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "admin", "oldpassword": "secret",
                  "password": "123123123ewq",
                  "_retype_password": "123123123qwe"}
        result = app.post("/users/changepassword/1", params=values, status=200)
        transaction_rollback(app)

    def test_change_password_tooshort(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"login": "admin", "oldpassword": "secret",
                  "password": "123123123",
                  "_retype_password": "123123123"}
        result = app.post("/users/changepassword/1", params=values, status=200)
        transaction_rollback(app)


@pytest.mark.incremental
class TestSetStandin:

    def test_create(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        create_user(app, "test")

        # Regression test for Issue1201 in Intevation waskiq tracker. If
        # the login is changed calling the setstandin page failed for
        # admin users.
        user = search_data(app, "users", "login", "test")
        user["login"] = "test123"
        app.post("/users/update/%s" % user["id"], params=user, status=302)

    def test_setstandin(self, app):
        user = search_data(app, "users", "login", "test123")
        app.get("/usergroups/setstandin/%s" % user["default_gid"])

        admin = search_data(app, "users", "login", "admin")
        app.post("/usergroups/setstandin/%s" % user["default_gid"],
                 params={"members": [admin["id"], user["id"]]}, status=302)

        app.get("/")
        transaction_rollback(app)


class TestChangeLogin:
    """Will check if the name of the users usergroup also changes if the
    login of the user changes."""

    def test_create(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        create_user(app, "test")
        user = search_data(app, "users", "login", "test")
        user["login"] = "test123"
        app.post("/users/update/%s" % user["id"], params=user, status=302)
        usergroup = search_data(app, "usergroups", "name", user["login"])
        assert usergroup
        app.get("/")
        transaction_rollback(app)


class TestRemoveAccount:
    """Will check if a registered user can delete his own account."""

    def test_unauthenticated(self, app):
        """Methods is called as unautheticated user"""
        logout(app)
        transaction_begin(app)
        app.get("/users/removeaccount/1", status=401)
        app.get("/")
        transaction_rollback(app)

    def test_unauthorized(self, app):
        """Method is called with a different uid than the id uf the
        current user. This is not allowed the users are only allowed to
        delete their own account."""
        login(app, "admin", "secret")
        transaction_begin(app)
        create_user(app, "test")
        user = search_data(app, "users", "login", "test")
        app.get("/users/removeaccount/%s" % user["id"], params=user, status=403)
        app.get("/")
        transaction_rollback(app)

    def test_unconfirmed(self, app):
        """User must confirm the deletion twice"""
        transaction_begin(app)
        login(app, "admin", "secret")
        create_user(app, "test")
        user = search_data(app, "users", "login", "test")
        login(app, "test", "123123123qwe")
        app.get("/users/removeaccount/%s" % user["id"], status=200)
        params = {}
        app.post("/users/removeaccount/%s" % user["id"], params=params, status=200)
        params = {"_confirm_remove_account": ["1"]}
        app.post("/users/removeaccount/%s" % user["id"], params=params, status=200)
        params = {"_confirm_remove_account2": ["1"]}
        app.post("/users/removeaccount/%s" % user["id"], params=params, status=200)
        app.get("/")
        transaction_rollback(app)

    def test_confirmed(self, app):
        """User must confirm the deletion twice"""
        transaction_begin(app)
        login(app, "admin", "secret")
        create_user(app, "test")
        user = search_data(app, "users", "login", "test")
        login(app, "test", "123123123qwe")

        app.get("/users/removeaccount/%s" % user["id"], status=200)
        params = {"_confirm_remove_account2": ["1"], "_confirm_remove_account": ["1"]}
        app.post("/users/removeaccount/%s" % user["id"], params=params, status=302)

        app.get("/")
        transaction_rollback(app)
