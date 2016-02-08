#!/usr/bin/env python
# encoding: utf-8
import pytest
from pytest_ringo import login, transaction_begin, transaction_rollback


class TestList:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/forms/list")


class TestRead:

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/forms/read/1")


class TestCreate:

    def test_GET(self, app):
        login(app, "admin", "secret")
        app.get("/forms/create")

    @pytest.mark.xfail
    def test_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"title": "test", "definiton": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'}
        app.post("/forms/create", params=values, status=302)
        transaction_rollback(app)

    @pytest.mark.xfail
    def test_POST_missing_title(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"title": "", "definiton": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'}
        app.post("/forms/create", params=values, status=200)
        transaction_rollback(app)

    @pytest.mark.xfail
    def test_POST_missing_definition(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"title": "test", "definiton": ''}
        app.post("/forms/create", params=values, status=200)
        transaction_rollback(app)


class TestUpdate:

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_update(self, app):
        login(app, "admin", "secret")
        app.get("/forms/update/1")

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_update_POST(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"title": "test", "definiton": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'}
        app.post("/forms/update/1", params=values, status=302)
        transaction_rollback(app)

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_update_POST_missing_title(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"title": "", "definiton": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'}
        app.post("/forms/update/1", params=values, status=200)
        transaction_rollback(app)

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_update_POST_missing_defintion(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"title": "test", "definiton": ''}
        app.post("/forms/update/1", params=values, status=200)
        transaction_rollback(app)


class TestDelete:

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_delete(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        app.get("/forms/delete/2")
        transaction_rollback(app)

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_delete_POST_confirm_yes(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/forms/delete/2", params=values, status=302)
        transaction_rollback(app)

    # FIXME: There is currently no form in the database () <2016-02-08 10:30> 
    @pytest.mark.xfail
    def test_delete_POST_admin_confirm_yes(self, app):
        login(app, "admin", "secret")
        transaction_begin(app)
        values = {"confirmed": 1}
        app.post("/forms/delete/1", params=values, status=302)
        transaction_rollback(app)
