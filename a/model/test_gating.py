from a.model import gating


class TestGating:
    def test_is_feature_enable(self):
        assert gating.is_feature_enabled("some_feature") == False

    def test_enable_feature(self):
        gating.enable_feature("some_feature")
        assert gating.is_feature_enabled("some_feature") == True
