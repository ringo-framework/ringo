#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


class TestList:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/modules/list")


class TestRead:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/modules/read/1")


class TestCreate:

    def test_GET(self, app):
        """Creating of new modules is not supported in the webinterface"""
        login(app, "admin", "secret")
        app.get("/modules/create", status=404)


class TestUpdate:

    def test_update(self, app):
        login(app, "admin", "secret")
        app.get("/modules/update/1")

    def test_update_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "modules", "label": "Modul",
                  "label_plural": "Modules"}
        app.post("/modules/update/1", params=values, status=302)
        transaction_rollback(app)

    @pytest.mark.xfail
    def test_update_POST_name_not_unique(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "users", "label": "Modul",
                  "label_plural": "Modules"}
        app.post("/modules/update/1", params=values, status=200)
        transaction_rollback(app)

    def test_update_POST_missing_name(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "", "label": "Modul",
                  "label_plural": "Modules"}
        app.post("/modules/update/1", params=values, status=200)
        transaction_rollback(app)

    def test_update_POST_missing_label(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "modules", "label": "",
                  "label_plural": "Modules"}
        app.post("/modules/update/1", params=values, status=200)
        transaction_rollback(app)

    def test_update_POST_missing_label_plural(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "modules", "label": "Modul",
                  "label_plural": ""}
        app.post("/modules/update/1", params=values, status=200)
        transaction_rollback(app)


class TestDelete:

    def test_delete(self, app):
        """Deleting of modules is not supported in the webinterface"""
        login(app, "admin", "secret")
        transaction_begin(app)
        app.get("/modules/delete/1", status=404)
        transaction_rollback(app)
