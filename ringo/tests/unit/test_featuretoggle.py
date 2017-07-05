class TestFeatureToggle:

    def test_enabled(self, apprequest):
        from ringo.lib.request.app import RingoRequest
        apprequest.ringo = RingoRequest(apprequest)
        assert apprequest.ringo.feature.enabled == True

    def test_disabled(self, apprequest):
        from ringo.lib.request.app import RingoRequest
        apprequest.ringo = RingoRequest(apprequest)
        assert apprequest.ringo.feature.disabled == False

    def test_missing(self, apprequest):
        from ringo.lib.request.app import RingoRequest
        apprequest.ringo = RingoRequest(apprequest)
        assert apprequest.ringo.feature.missing == False
