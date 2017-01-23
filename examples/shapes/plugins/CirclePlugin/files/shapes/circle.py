from shape import Shape


class Circle(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "Circle"
        self.sides = None
        self.is_polygon = False

    @property
    def shape_is_a_polygon(self):
        return "A Circle is not a polygon!"

    def area(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()
