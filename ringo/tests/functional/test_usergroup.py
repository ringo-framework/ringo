#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


class TestList:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/usergroups/list")


class TestRead:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/usergroups/read/1")


class TestCreate:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/usergroups/create")

    def test_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "test"}
        app.post("/usergroups/create", params=values, status=302)
        transaction_rollback(app)

    @pytest.mark.xfail
    def test_POST_existing_group(self, app):
        # FIXME: https://github.com/ringo-framework/ringo/issues/4 (ti) <2016-01-18 16:46> 
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "admins"}
        app.post("/usergroups/create", params=values, status=200)
        transaction_rollback(app)


class TestUpdate:

    def test_update(self, app):
        login(app, "admin", "secret")
        app.get("/usergroups/update/1")

    def test_update_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "adminstest"}
        app.post("/usergroups/update/1", params=values, status=302)
        transaction_rollback(app)

    def test_update_POST_missing_name(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": ""}
        app.post("/usergroups/update/1", params=values, status=200)
        transaction_rollback(app)


class TestDelete:

    def test_delete(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        app.get("/usergroups/delete/2")
        transaction_rollback(app)

    def test_delete_POST_confirm_yes(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/usergroups/delete/2", params=values, status=302)
        transaction_rollback(app)

    @pytest.mark.xfail
    def test_delete_POST_admin_confirm_yes(self, app):
        # FIXME: https://github.com/ringo-framework/ringo/issues/5 (ti) <2016-01-18 16:46> 
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/usergroups/delete/1", params=values, status=302)
        transaction_rollback(app)
