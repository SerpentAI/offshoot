import offshoot


class TestInvalidPlugin(offshoot.Plugin):
    name = "TestInvalidPlugin"
    version = "0.1.0"

    libraries = [
        "requests"
    ]

    files = [
        {"path": "test_plugin_pluggable_expected.py", "pluggable": "TestPluggable"},
        {"path": "test_plugin_pluggable_accepted.py", "pluggable": "TestPluggable"},
        {"path": "test_plugin_pluggable_forbidden.py", "pluggable": "TestPluggable"}
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
    offshoot.executable_hook(TestInvalidPlugin)
