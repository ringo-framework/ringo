#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


class TestList:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/profiles/list")


class TestRead:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/profiles/read/1")


class TestCreate:

    def test_GET(self, app):
        """Creation of profiles is not supported in the webinterface"""
        login(app, "admin", "secret")
        app.get("/profiles/create", status=404)


class TestUpdate:

    def test_update(self, app):
        login(app, "admin", "secret")
        app.get("/profiles/update/1")

    def test_update_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"email": "foo@bar.de"}
        app.post("/profiles/update/1", params=values, status=302)
        transaction_rollback(app)

    def test_update_POST_missing_email(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"email": ""}
        app.post("/profiles/update/1", params=values, status=200)
        transaction_rollback(app)


class TestDelete:

    def test_delete(self, app):
        """Deletion of profiles is not supported in the webinterface"""
        login(app, "admin", "secret")
        transaction_begin(app)
        app.get("/profiles/delete/1", status=404)
        transaction_rollback(app)
