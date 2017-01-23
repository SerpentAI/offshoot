import pluggable


class TestPluginPluggableExpected(pluggable.TestPluggable):
    def accepted_function(self):
        raise NotImplementedError()
