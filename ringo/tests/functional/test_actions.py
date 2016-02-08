#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


class TestList:

    def test_GET(self, app):
        """Listing of actions is not supported in the webinterface"""
        login(app, "admin", "secret")
        app.get("/actions/list", status=404)


class TestRead:

    def test_GET(self, app):
        """Reading of actions is not supported in the webinterface"""
        login(app, "admin", "secret")
        app.get("/actions/read/1", status=404)


class TestCreate:

    def test_GET(self, app):
        """Creation of actions is not supported in the webinterface"""
        login(app, "admin", "secret")
        app.get("/actions/create", status=404)


class TestUpdate:

    def test_update(self, app):
        """Updating of actions is not supported in the webinterface"""
        login(app, "admin", "secret")
        app.get("/actions/update/1", status=404)


class TestDelete:

    def test_delete(self, app):
        """Deletion of actions is not supported in the webinterface"""
        login(app, "admin", "secret")
        transaction_begin(app)
        app.get("/actions/delete/1", status=404)
        transaction_rollback(app)
