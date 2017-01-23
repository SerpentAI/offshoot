from shape import Shape


class Triangle(Shape):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "Triangle"
        self.sides = 3
        self.is_polygon = True

    def area(self):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()
