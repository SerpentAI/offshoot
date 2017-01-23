import offshoot


class Shape(offshoot.Pluggable):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = kwargs.get("name") or "Shape"
        self.sides = kwargs.get("sides") or 0
        self.is_polygon = kwargs.get("is_polygon") or True

    @property
    def shape_name(self):
        return "Shape: %s" % self.name

    @property
    def shape_sides(self):
        return "Sides: %d" % self.sides

    @property
    @offshoot.accepted
    def shape_is_a_polygon(self):
        return "I AM polygon" if self.is_polygon else "I AM NOT a polygon"

    @offshoot.expected
    def area(self):
        raise NotImplementedError()

    @offshoot.expected
    def draw(self):
        raise NotImplementedError()

    def lol(self):
        print("lol")

    @offshoot.forbidden
    def rofl(self):
        print("rofl")

    @classmethod
    def on_file_install(cls, **kwargs):
        print(kwargs)

    @classmethod
    def on_file_uninstall(cls, **kwargs):
        print(kwargs)
