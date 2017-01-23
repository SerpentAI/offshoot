import offshoot


class TestPluggable(offshoot.Pluggable):

    @offshoot.expected
    def expected_function(self):
        raise NotImplementedError()

    @offshoot.accepted
    def accepted_function(self):
        raise NotImplementedError()

    @offshoot.forbidden
    def forbidden_function(self):
        raise NotImplementedError()


class TestPluggableInvalid():
    pass
