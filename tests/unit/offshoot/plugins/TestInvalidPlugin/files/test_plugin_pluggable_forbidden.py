import pluggable


class TestPluginPluggableExpected(pluggable.TestPluggable):
    def forbidden_function(self):
        raise NotImplementedError()
