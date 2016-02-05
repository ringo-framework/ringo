#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


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
        values = {"login": "test",
                  "password": "123123123qwe",
                  "_retype_password": "123123123qwe",
                  "_first_name": u"Först", "_last_name": "Last",
                  "_email": "email@example.com"}
        app.post("/users/create", params=values, status=302)
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
        transaction_rollback(app)
