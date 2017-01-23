from shape import Shape


class Star(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "Star"
        self.sides = 10
        self.is_polygon = True

    @property
    def shape_is_a_polygon(self):
        return "A Star is a polygon!"

    def area(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()
