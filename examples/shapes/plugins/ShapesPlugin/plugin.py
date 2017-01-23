import offshoot


class ShapesPlugin(offshoot.Plugin):
    name = "ShapesPlugin"
    version = "0.1.0"

    libraries = [
        "requests",
        "requests-respectful",
        "elasticsearch"
    ]

    files = [
        {"path": "shapes/rectangle.py", "pluggable": "Shape"},
        {"path": "shapes/triangle.py", "pluggable": "Shape"},
        {"path": "shapes/star.py", "pluggable": "Shape"}
    ]

    config = {
        "bot_uprising": {
            "happening": True,
            "casualties": 4523857
        },
        "fruit": ["apple", "pear", "orange"],
        "answer": 42,
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)


if __name__ == "__main__":
    offshoot.executable_hook(ShapesPlugin)
