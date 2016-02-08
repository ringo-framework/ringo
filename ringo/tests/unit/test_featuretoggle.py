class TestFeatureToggle:

    def test_enabled(self, apprequest):
        assert apprequest.ringo.feature.enabled == True

    def test_disabled(self, apprequest):
        assert apprequest.ringo.feature.disabled == False

    def test_missing(self, apprequest):
        assert apprequest.ringo.feature.missing == False
