import offshoot


class CirclePlugin(offshoot.Plugin):
    name = "CirclePlugin"
    version = "0.1.0"

    libraries = [
        "invoke"
    ]

    files = [
        {"path": "shapes/circle.py", "pluggable": "Shape"}
    ]

    config = {
        "count": 12345,
        "digits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)


if __name__ == "__main__":
    offshoot.executable_hook(CirclePlugin)
