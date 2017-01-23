import offshoot


class TestPlugin(offshoot.Plugin):
    name = "TestPlugin"
    version = "0.1.0"

    libraries = [
        "requests"
    ]

    files = [
        {"path": "test_plugin_pluggable_expected.py", "pluggable": "TestPluggable"}
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
    offshoot.executable_hook(TestPlugin)
