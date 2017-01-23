from shape import Shape


class Square(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "Square"
        self.sides = 4
        self.is_polygon = True

    @property
    def shape_is_a_polygon(self):
        return "A Square is a polygon!"

    def area(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()
