import pluggable


class TestPluginPluggableExpected(pluggable.TestPluggable):
    def expected_function(self):
        raise NotImplementedError()
