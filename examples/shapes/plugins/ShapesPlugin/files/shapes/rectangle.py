from shape import Shape


class Rectangle(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "Rectangle"
        self.sides = 4
        self.is_polygon = True

    @property
    def shape_is_a_polygon(self):
        return "A Rectangle is a polygon!"

    def area(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()
