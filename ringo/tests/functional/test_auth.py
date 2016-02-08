class TestLogin:

    def test_logout(self, app):
        app.get("/auth/logout")

    def test_login(self, app):
        app.get("/auth/login")

    def test_login_ok(self, app):
        app.post("/auth/login",
                 params={"login": "admin", "pass": "secret"},
                 status=302)

    def test_login_failed(self, app):
        app.post("/auth/login",
                 params={"login": "admin", "pass": "wrong"},
                 status=200)

    def test_logininfo_after_5_failed(self, app):
        """Check if the loginwarning is shown on login after five failed
        logins before"""
        for i in range(5):
            app.post("/auth/login", params={"login": "admin", "pass": "wrong"})
        response = app.post("/auth/login",
                            params={"login": "admin", "pass": "secret"},
                            status=302).follow()
        assert "attempt of misuse" in response
