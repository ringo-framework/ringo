#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


class TestList:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/roles/list")


class TestRead:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/roles/read/1")


class TestCreate:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/roles/create")

    def test_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "test", "label": "test"}
        app.post("/roles/create", params=values, status=302)
        transaction_rollback(app)

    @pytest.mark.xfail
    def test_POST_existing_group(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "admin", "label": "admin"}
        app.post("/roles/create", params=values, status=200)
        transaction_rollback(app)


class TestUpdate:

    def test_update(self, app):
        login(app, "admin", "secret")
        app.get("/roles/update/1")

    def test_update_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "admintest", "label": "admintest"}
        app.post("/roles/update/1", params=values, status=302)
        transaction_rollback(app)

    def test_update_POST_missing_name(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "", "label": "Admin"}
        app.post("/roles/update/1", params=values, status=200)
        transaction_rollback(app)

    def test_update_POST_missing_label(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"name": "admin", "label": ""}
        app.post("/roles/update/1", params=values, status=200)
        transaction_rollback(app)


class TestDelete:

    def test_delete(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        app.get("/roles/delete/2")
        transaction_rollback(app)

    def test_delete_POST_confirm_yes(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/roles/delete/2", params=values, status=302)
        transaction_rollback(app)

    def test_delete_POST_admin_confirm_yes(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/roles/delete/1", params=values, status=302)
        transaction_rollback(app)
