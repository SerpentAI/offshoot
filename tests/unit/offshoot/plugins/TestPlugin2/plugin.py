import offshoot


class TestPlugin2(offshoot.Plugin):
    name = "TestPlugin2"
    version = "0.1.0"

    plugins = ["TestPlugin"]

    libraries = [
        "requests"
    ]

    files = [
        {"path": "test_plugin_pluggable.py", "pluggable": "TestPluggable"}
    ]

    config = {
        "is_test": True
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)


if __name__ == "__main__":
    offshoot.executable_hook(TestPlugin2)
