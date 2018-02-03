# -*- coding: utf-8 -*-
import pytest

import offshoot

from pluggable import TestPluggable

from plugins.TestPlugin.plugin import TestPlugin
from plugins.TestPlugin2.plugin import TestPlugin2

from plugins.TestInvalidPlugin.plugin import TestInvalidPlugin

import yaml
import subprocess
import types
import os
import os.path
import inspect
import json


# Tests
def test_setup():
    os.symlink("tests/unit/offshoot/plugins", "plugins")
    os.symlink("tests/unit/offshoot/config", "config")
    os.symlink("tests/unit/offshoot/libraries", "libraries")


def test_importing_the_module_should_expose_a_config_variable():
    assert hasattr(offshoot, "config")
    assert isinstance(offshoot.config, dict)


def test_importing_the_module_should_expose_a_lambda_to_map_pluggable_classes():
    assert hasattr(offshoot, "pluggable_classes")
    assert isinstance(offshoot.pluggable_classes, types.LambdaType)


def test_importing_the_module_should_expose_the_functions_from_base():
    assert hasattr(offshoot, "validate_plugin_file")
    assert hasattr(offshoot, "installed_plugins")
    assert hasattr(offshoot, "discover")

    assert isinstance(offshoot.validate_plugin_file, types.FunctionType)
    assert isinstance(offshoot.installed_plugins, types.FunctionType)
    assert isinstance(offshoot.discover, types.FunctionType)


def test_base_should_provide_a_function_to_get_a_default_and_complete_configuration():
    assert hasattr(offshoot, "default_configuration")
    assert isinstance(offshoot.default_configuration, types.FunctionType)

    config = offshoot.default_configuration()

    assert isinstance(config, dict)

    assert "modules" in config
    assert "file_paths" in config
    assert "allow" in config
    assert "sandbox_configuration_keys" in config


def test_base_should_be_able_to_load_a_configuration_from_an_existing_file():
    config = offshoot.default_configuration()

    config["modules"].append("test")
    config["sandbox_configuration_keys"] = False
    config["allow"]["callbacks"] = False

    with open("offshoot.test.yml", "w") as f:
        yaml.dump(config, f)

    loaded_config = offshoot.load_configuration("offshoot.test.yml")

    assert isinstance(loaded_config, dict)

    assert "test" in loaded_config["modules"]
    assert loaded_config["sandbox_configuration_keys"] is False
    assert loaded_config["allow"]["callbacks"] is False

    subprocess.call(["rm", "-f", "offshoot.test.yml"])


def test_base_should_load_the_default_configuration_if_the_configuration_file_does_not_exist():
    config = offshoot.load_configuration("offshoot.test.yml")

    assert isinstance(config, dict)

    assert len(config["modules"]) == 0
    assert config["sandbox_configuration_keys"] is True
    assert config["allow"]["callbacks"] is True


def test_base_should_be_able_to_generate_a_configuration_file():
    offshoot.generate_configuration_file()
    assert os.path.isfile("offshoot.yml")

    config = offshoot.load_configuration("offshoot.yml")

    assert isinstance(config, dict)

    assert len(config["modules"]) == 0
    assert config["sandbox_configuration_keys"] is True
    assert config["allow"]["callbacks"] is True

    subprocess.call(["rm", "-f", "offshoot.yml"])


def test_base_should_be_able_to_extract_pluggable_classes_according_to_the_configuration():
    config = offshoot.default_configuration()

    assert isinstance(offshoot.map_pluggable_classes(config), dict)
    assert len(offshoot.map_pluggable_classes(config)) == 0

    config["modules"].append("pluggable")

    pluggable_classes = offshoot.map_pluggable_classes(config)

    assert isinstance(pluggable_classes, dict)

    assert "TestPluggable" in pluggable_classes
    assert "TestPluggableInvalid" not in pluggable_classes

    assert inspect.isclass(pluggable_classes["TestPluggable"])


def test_base_should_be_able_to_validate_a_plugin_file_according_to_its_pluggable():
    config = offshoot.default_configuration()
    config["modules"].append("pluggable")

    pluggable_classes = offshoot.map_pluggable_classes(config)

    validation_result = offshoot.validate_plugin_file(
        "tests/unit/offshoot/plugins/TestPlugin/files/test_plugin_pluggable.py",
        "TestPluggable",
        pluggable_classes["TestPluggable"].method_directives()
    )

    assert validation_result[0] is False
    assert "expected methods are missing" in validation_result[1][0]

    validation_result = offshoot.validate_plugin_file(
        "tests/unit/offshoot/plugins/TestPlugin/files/test_plugin_pluggable_expected.py",
        "TestPluggable",
        pluggable_classes["TestPluggable"].method_directives()
    )

    assert validation_result[0] is True
    assert len(validation_result[1]) == 0

    validation_result = offshoot.validate_plugin_file(
        "tests/unit/offshoot/plugins/TestPlugin/files/test_plugin_pluggable_accepted.py",
        "TestPluggable",
        pluggable_classes["TestPluggable"].method_directives()
    )

    assert validation_result[0] is False
    assert "expected methods are missing" in validation_result[1][0]

    validation_result = offshoot.validate_plugin_file(
        "tests/unit/offshoot/plugins/TestPlugin/files/test_plugin_pluggable_forbidden.py",
        "TestPluggable",
        pluggable_classes["TestPluggable"].method_directives()
    )

    assert validation_result[0] is False

    expected_messages = {
        "expected methods are missing",
        "method should not appear in the class"
    }

    for validation_message in validation_result[1]:
        for expected_message in list(expected_messages):
            if expected_message in validation_message:
                expected_messages.remove(expected_message)

    assert len(expected_messages) == 0


def test_base_should_be_able_to_return_a_list_of_installed_plugins():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.uninstall()

    assert len(offshoot.installed_plugins()) == 0

    TestPlugin.install()

    assert len(offshoot.installed_plugins()) == 1
    assert "TestPlugin - 0.1.0" in offshoot.installed_plugins()

    TestPlugin.uninstall()

    assert len(offshoot.installed_plugins()) == 0

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_base_should_be_able_to_discover_installed_plugins_for_a_specified_pluggable():
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    offshoot.config["modules"].append("pluggable")

    TestPlugin.install()

    class_mapping = offshoot.discover("TestPluggable", globals())

    assert isinstance(class_mapping, dict)
    assert len(class_mapping) == 0

    assert inspect.isclass(TestPluginPluggableExpected)

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_base_should_be_able_to_discover_installed_plugins_for_a_specified_pluggable_with_no_scope_passed_along():
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    offshoot.config["modules"].append("pluggable")

    TestPlugin.install()

    class_mapping = offshoot.discover("TestPluggable")

    assert isinstance(class_mapping, dict)

    assert len(class_mapping) == 1
    assert "TestPluginPluggableExpected" in class_mapping
    assert inspect.isclass(class_mapping["TestPluginPluggableExpected"])

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_base_should_be_able_to_discover_installed_plugins_for_a_specified_pluggable_with_selection_passed_along():
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    offshoot.config["modules"].append("pluggable")

    TestPlugin.install()

    class_mapping = offshoot.discover("TestPluggable", selection="123")

    assert isinstance(class_mapping, dict)
    assert len(class_mapping) == 0

    class_mapping = offshoot.discover("TestPluggable", selection=["123"])

    assert isinstance(class_mapping, dict)
    assert len(class_mapping) == 0

    class_mapping = offshoot.discover("TestPluggable", selection=["TestPluginPluggableExpected"])

    assert isinstance(class_mapping, dict)
    assert len(class_mapping) == 1
    assert "TestPluginPluggableExpected" in class_mapping
    assert inspect.isclass(class_mapping["TestPluginPluggableExpected"])

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_base_should_be_able_to_determine_if_a_file_implements_a_specified_pluggable():
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    offshoot.config["modules"].append("pluggable")

    TestPlugin.install()

    manifest = offshoot.Manifest()
    files = manifest.plugin_files_for_pluggable("TestPluggable")

    valid, plugin_class = offshoot.file_contains_pluggable(files[0][0], "TestPluggable")

    assert valid is True
    assert plugin_class == "TestPluginPluggableExpected"

    valid, plugin_class = offshoot.file_contains_pluggable("INVALID.txt", "TestPluggable")

    assert valid is False
    assert plugin_class is None

    valid, plugin_class = offshoot.file_contains_pluggable(files[0][0], "InvalidPluggable")

    assert valid is False
    assert plugin_class is None

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_base_magic_decorators_should_not_do_anything():
    func = "I AM FUNCTION"

    assert offshoot.accepted(func) == "I AM FUNCTION"
    assert offshoot.expected(func) == "I AM FUNCTION"
    assert offshoot.forbidden(func) == "I AM FUNCTION"


def test_manifest_should_create_manifest_file_if_it_does_not_exist_on_initialization():
    os.remove("offshoot.manifest.json")

    offshoot.Manifest()
    assert os.path.isfile("offshoot.manifest.json")

    with open("offshoot.manifest.json", "r") as f:
        assert "plugins" in json.loads(f.read())


def test_manifest_should_be_able_to_list_installed_plugins_along_with_their_metadata():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.install()

    manifest = offshoot.Manifest()
    plugins = manifest.list_plugins()

    assert "TestPlugin" in plugins

    assert plugins["TestPlugin"].get("name") == "TestPlugin"
    assert plugins["TestPlugin"].get("version") == "0.1.0"

    assert "files" in plugins["TestPlugin"]
    assert "config" in plugins["TestPlugin"]
    assert "libraries" in plugins["TestPlugin"]

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_manifest_should_be_able_to_determine_if_a_specific_plugin_is_installed():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.install()

    manifest = offshoot.Manifest()
    assert manifest.contains_plugin("TestPlugin")

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_manifest_should_be_able_to_add_a_plugin_and_its_metadata():
    os.remove("offshoot.manifest.json")

    manifest = offshoot.Manifest()

    manifest.add_plugin("TestPlugin")
    plugins = manifest.list_plugins()

    assert "TestPlugin" in plugins

    assert plugins["TestPlugin"].get("name") == "TestPlugin"
    assert plugins["TestPlugin"].get("version") == "0.1.0"

    assert "files" in plugins["TestPlugin"]
    assert "config" in plugins["TestPlugin"]
    assert "libraries" in plugins["TestPlugin"]


def test_manifest_should_be_able_to_remove_a_plugin_and_its_metadata():
    manifest = offshoot.Manifest()
    plugins = manifest.list_plugins()

    assert "TestPlugin" in plugins

    assert plugins["TestPlugin"].get("name") == "TestPlugin"
    assert plugins["TestPlugin"].get("version") == "0.1.0"

    assert "files" in plugins["TestPlugin"]
    assert "config" in plugins["TestPlugin"]
    assert "libraries" in plugins["TestPlugin"]

    manifest.remove_plugin("TestPlugin")

    assert len(manifest.list_plugins()) == 0

    os.remove("offshoot.manifest.json")


def test_manifest_should_be_able_to_return_all_file_names_containing_a_specific_pluggable():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.install()

    manifest = offshoot.Manifest()
    plugin_files = manifest.plugin_files_for_pluggable("TestPluggable")

    assert len(plugin_files) == 1

    assert plugin_files[0][0] == "plugins/TestPlugin/files/test_plugin_pluggable_expected.py"
    assert plugin_files[0][1] == "TestPluggable"

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_pluggable_should_be_able_to_return_its_method_directives():
    method_directives = TestPluggable.method_directives()

    assert "expected" in method_directives
    assert "accepted" in method_directives
    assert "forbidden" in method_directives

    assert "expected_function" in method_directives["expected"]
    assert "accepted_function" in method_directives["accepted"]
    assert "forbidden_function" in method_directives["forbidden"]


def test_pluggable_should_be_able_to_determine_the_methods_tagged_with_a_specific_decorator():
    assert "expected_function" in TestPluggable.methods_with_decorator("expected")
    assert "accepted_function" not in TestPluggable.methods_with_decorator("expected")
    assert "forbidden_function" not in TestPluggable.methods_with_decorator("expected")

    assert "expected_function" not in TestPluggable.methods_with_decorator("accepted")
    assert "accepted_function" in TestPluggable.methods_with_decorator("accepted")
    assert "forbidden_function" not in TestPluggable.methods_with_decorator("accepted")

    assert "expected_function" not in TestPluggable.methods_with_decorator("forbidden")
    assert "accepted_function" not in TestPluggable.methods_with_decorator("forbidden")
    assert "forbidden_function" in TestPluggable.methods_with_decorator("forbidden")


def test_pluggable_should_trigger_a_callback_on_file_install(mocker):
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False

    mocker.spy(TestPluggable, "on_file_install")

    TestPlugin.install()

    assert TestPluggable.on_file_install.call_count == 1

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True


def test_pluggable_should_trigger_a_callback_on_file_uninstall(mocker):
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False

    mocker.spy(TestPluggable, "on_file_uninstall")

    TestPlugin.install()
    TestPlugin.uninstall()

    assert TestPluggable.on_file_uninstall.call_count == 1

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True


def test_plugin_respects_configuration_allow_flags_on_install(mocker):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPlugin, "install_files")
    mocker.spy(TestPlugin, "install_configuration")
    mocker.spy(TestPlugin, "install_libraries")
    mocker.spy(TestPlugin, "on_install")

    TestPlugin.install()

    assert TestPlugin.install_files.call_count == 0
    assert TestPlugin.install_configuration.call_count == 0
    assert TestPlugin.install_libraries.call_count == 0
    assert TestPlugin.on_install.call_count == 0

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True

    TestPlugin.install()

    assert TestPlugin.install_files.call_count == 1
    assert TestPlugin.install_configuration.call_count == 1
    assert TestPlugin.install_libraries.call_count == 1
    assert TestPlugin.on_install.call_count == 1

    TestPlugin.uninstall()


def test_plugin_adds_a_manifest_entry_on_install(monkeypatch):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    global add_plugin_called
    add_plugin_called = False

    class MockManifest:
        def add_plugin(self, name):
            global add_plugin_called
            add_plugin_called = True

    manifest = MockManifest()
    monkeypatch.setattr(offshoot.Manifest, "add_plugin", manifest.add_plugin)

    TestPlugin.install()

    assert add_plugin_called

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_respects_configuration_allow_flags_on_uninstall(mocker):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPlugin, "uninstall_files")
    mocker.spy(TestPlugin, "uninstall_configuration")
    mocker.spy(TestPlugin, "uninstall_libraries")
    mocker.spy(TestPlugin, "on_uninstall")

    TestPlugin.install()
    TestPlugin.uninstall()

    assert TestPlugin.uninstall_files.call_count == 0
    assert TestPlugin.uninstall_configuration.call_count == 0
    assert TestPlugin.uninstall_libraries.call_count == 0
    assert TestPlugin.on_uninstall.call_count == 0

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True

    TestPlugin.install()
    TestPlugin.uninstall()

    assert TestPlugin.uninstall_files.call_count == 1
    assert TestPlugin.uninstall_configuration.call_count == 1
    assert TestPlugin.uninstall_libraries.call_count == 1
    assert TestPlugin.on_uninstall.call_count == 1


def test_plugin_removes_a_manifest_entry_on_uninstall(monkeypatch):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    global remove_plugin_called
    remove_plugin_called = False

    class MockManifest:
        def remove_plugin(self, name):
            global remove_plugin_called
            remove_plugin_called = True

    manifest = MockManifest()
    monkeypatch.setattr(offshoot.Manifest, "remove_plugin", manifest.remove_plugin)

    TestPlugin.install()
    TestPlugin.uninstall()

    assert remove_plugin_called

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_files_are_validated_against_the_pluggable_specification_on_file_install(mocker):
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPlugin, "_validate_file_for_pluggable")

    TestPlugin.install()

    TestPlugin._validate_file_for_pluggable.assert_called_once_with(
        "plugins/TestPlugin/files/test_plugin_pluggable_expected.py",
        "TestPluggable"
    )

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_files_are_uninstalled_on_file_install_error(mocker, monkeypatch):
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPluggable, "on_file_uninstall")

    global remove_plugin_called
    remove_plugin_called = False

    class MockManifest:
        def remove_plugin(self, name):
            global remove_plugin_called
            remove_plugin_called = True

    manifest = MockManifest()
    monkeypatch.setattr(offshoot.Manifest, "remove_plugin", manifest.remove_plugin)

    with pytest.raises(offshoot.PluginError):
        TestInvalidPlugin.install()

    assert TestPluggable.on_file_uninstall.call_count == 1
    assert remove_plugin_called

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_file_install_callbacks_are_sent_on_file_install(mocker):
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPluggable, "on_file_install")

    TestPlugin.install()

    assert TestPluggable.on_file_install.call_count == 1
    TestPluggable.on_file_install.assert_called_once_with(
        path="test_plugin_pluggable_expected.py",
        pluggable="TestPluggable"
    )

    TestPlugin.uninstall()

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_file_uninstall_callbacks_are_sent_on_file_uninstall(mocker):
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPluggable, "on_file_uninstall")

    TestPlugin.install()
    TestPlugin.uninstall()

    assert TestPluggable.on_file_uninstall.call_count == 1
    TestPluggable.on_file_uninstall.assert_called_once_with(
        path="test_plugin_pluggable_expected.py",
        pluggable="TestPluggable"
    )

    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_an_error_should_be_raised_on_configuration_install_if_the_configuration_directory_is_absent():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    os.remove("config")

    with pytest.raises(offshoot.PluginError):
        TestPlugin.install()

    os.symlink("tests/unit/offshoot/config", "config")

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_nothing_should_happen_if_the_plugin_has_no_configuration_on_configuration_install():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.config = None
    assert TestPlugin.install_configuration() is None

    TestPlugin.config = {}
    assert TestPlugin.install_configuration() is None

    TestPlugin.config = {
        "is_test": True
    }

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_the_configuration_keys_should_be_written_as_is_if_the_configuration_file_does_not_exist_on_configuration_install():
    if os.path.isfile(offshoot.config["file_paths"]["config"]):
        os.remove(offshoot.config["file_paths"]["config"])

    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False
    offshoot.config["sandbox_configuration_keys"] = False

    TestPlugin.install()

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    assert "is_test" in config
    assert config["is_test"] is True

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True
    offshoot.config["sandbox_configuration_keys"] = True


def test_plugin_the_configuration_keys_should_be_merged_properly_with_an_existing_configuration_file_on_configuration_install():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False
    offshoot.config["sandbox_configuration_keys"] = False

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    config["is_extra"] = True

    with open(offshoot.config["file_paths"]["config"], "w") as f:
        yaml.dump(config, f)

    TestPlugin.install()

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    assert "is_test" in config
    assert config["is_test"] is True

    assert "is_extra" in config
    assert config["is_extra"] is True

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True
    offshoot.config["sandbox_configuration_keys"] = True


def test_plugin_the_configuration_keys_should_be_sandboxed_if_the_option_is_set_on_configuration_install():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.install()

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    assert "TestPlugin" in config
    assert "is_test" in config["TestPlugin"]
    assert config["TestPlugin"]["is_test"] is True

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_an_error_should_be_raised_on_configuration_uninstall_if_the_configuration_directory_is_absent():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    os.remove("config")

    with pytest.raises(offshoot.PluginError):
        TestPlugin.uninstall()

    os.symlink("tests/unit/offshoot/config", "config")

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_nothing_should_happen_if_the_plugin_has_no_configuration_on_configuration_uninstall():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.config = None
    assert TestPlugin.uninstall_configuration() is None

    TestPlugin.config = {}
    assert TestPlugin.uninstall_configuration() is None

    TestPlugin.config = {
        "is_test": True
    }

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_nothing_should_happen_if_the_plugin_configuration_file_does_not_exist_on_configuration_uninstall():
    if os.path.isfile(offshoot.config["file_paths"]["config"]):
        os.remove(offshoot.config["file_paths"]["config"])

    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    assert TestPlugin.uninstall_configuration() is None

    TestPlugin.install()
    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_the_configuration_keys_should_be_removed_properly_on_configuration_uninstall():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False
    offshoot.config["sandbox_configuration_keys"] = False

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    config["is_extra"] = True

    with open(offshoot.config["file_paths"]["config"], "w") as f:
        yaml.dump(config, f)

    TestPlugin.install()
    TestPlugin.uninstall()

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    assert "is_test" not in config

    assert "is_extra" in config
    assert config["is_extra"] is True

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True
    offshoot.config["sandbox_configuration_keys"] = True


def test_plugin_the_configuration_keys_should_be_removed_properly_if_the_sandbox_keys_option_is_set_on_configuration_uninstall():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.install()
    TestPlugin.uninstall()

    with open(offshoot.config["file_paths"]["config"], "r") as f:
        config = yaml.safe_load(f)

    assert "TestPlugin" not in config

    assert "is_extra" in config
    assert config["is_extra"] is True

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_an_error_should_be_raised_on_libraries_install_if_the_libraries_directory_is_absent():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["callbacks"] = False
    offshoot.config["file_paths"]["libraries"] = "libraries/requirements.plugins.txt"

    os.remove("libraries")

    with pytest.raises(offshoot.PluginError):
        TestPlugin.install()

    os.symlink("tests/unit/offshoot/libraries", "libraries")

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["callbacks"] = True
    offshoot.config["file_paths"]["libraries"] = "requirements.plugins.txt"


def test_plugin_nothing_should_happen_if_the_plugin_has_no_libraries_on_libraries_install():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.libraries = None
    assert TestPlugin.install_libraries() is None

    TestPlugin.libraries = []
    assert TestPlugin.install_libraries() is None

    TestPlugin.libraries = ["requests"]

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_should_add_a_libraries_block_on_libraries_install(mocker):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPlugin, "_write_plugin_requirement_blocks_to")

    TestPlugin.install()

    TestPlugin._write_plugin_requirement_blocks_to.assert_called_once_with(
        offshoot.config["file_paths"]["libraries"]
    )

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_an_error_should_be_raised_on_libraries_uninstall_if_the_libraries_directory_is_absent():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["callbacks"] = False
    offshoot.config["file_paths"]["libraries"] = "libraries/requirements.plugins.txt"

    os.remove("libraries")

    with pytest.raises(offshoot.PluginError):
        TestPlugin.uninstall()

    os.symlink("tests/unit/offshoot/libraries", "libraries")

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["callbacks"] = True
    offshoot.config["file_paths"]["libraries"] = "requirements.plugins.txt"


def test_plugin_nothing_should_happen_if_the_plugin_has_no_libraries_on_libraries_uninstall():
    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.libraries = None
    assert TestPlugin.uninstall_libraries() is None

    TestPlugin.libraries = []
    assert TestPlugin.uninstall_libraries() is None

    TestPlugin.libraries = ["requests"]

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_should_remove_a_libraries_block_on_libraries_uninstall(mocker):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["callbacks"] = False

    mocker.spy(TestPlugin, "_remove_plugin_requirement_block_from")

    TestPlugin.install()
    TestPlugin.uninstall()

    TestPlugin._remove_plugin_requirement_block_from.assert_called_once_with(
        offshoot.config["file_paths"]["libraries"]
    )

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_should_be_able_to_validate_a_file_against_a_pluggable_specification(mocker):
    mocker.spy(offshoot, "validate_plugin_file")

    TestPlugin._validate_file_for_pluggable(
        "plugins/TestPlugin/files/test_plugin_pluggable_expected.py",
        "TestPluggable"
    )

    offshoot.validate_plugin_file.assert_called_once_with(
        "plugins/TestPlugin/files/test_plugin_pluggable_expected.py",
        "TestPluggable",
        TestPluggable.method_directives()
    )


def test_plugin_should_be_able_to_generate_a_requirements_block_for_its_libraries():
    assert TestPlugin._generate_plugin_requirement_block() == ["### TestPlugin Requirements ###", "requests", "######"]
    assert TestInvalidPlugin._generate_plugin_requirement_block() == ["### TestInvalidPlugin Requirements ###", "requests", "######"]


def test_plugin_should_be_able_to_extract_all_requirement_blocks_from_its_libraries_file():
    TestPlugin.install_libraries()
    TestInvalidPlugin.install_libraries()

    requirement_blocks = TestPlugin._extract_plugin_requirement_blocks_from(offshoot.config["file_paths"]["libraries"])

    assert "TestPlugin Requirements" in requirement_blocks
    assert "TestInvalidPlugin Requirements" in requirement_blocks

    assert requirement_blocks["TestPlugin Requirements"] == TestPlugin._generate_plugin_requirement_block()
    assert requirement_blocks["TestInvalidPlugin Requirements"] == TestInvalidPlugin._generate_plugin_requirement_block()

    TestPlugin.uninstall_libraries()
    TestInvalidPlugin.uninstall_libraries()


def test_plugin_should_be_able_to_write_all_requirement_blocks_to_its_libraries_file():
    TestPlugin._write_plugin_requirement_blocks_to(offshoot.config["file_paths"]["libraries"])
    TestInvalidPlugin._write_plugin_requirement_blocks_to(offshoot.config["file_paths"]["libraries"])

    requirement_blocks = TestPlugin._extract_plugin_requirement_blocks_from(offshoot.config["file_paths"]["libraries"])

    assert "TestPlugin Requirements" in requirement_blocks
    assert "TestInvalidPlugin Requirements" in requirement_blocks

    assert requirement_blocks["TestPlugin Requirements"] == TestPlugin._generate_plugin_requirement_block()
    assert requirement_blocks["TestInvalidPlugin Requirements"] == TestInvalidPlugin._generate_plugin_requirement_block()


def test_plugin_should_be_able_to_remove_a_requirement_block_from_its_libraries_file():
    TestPlugin._remove_plugin_requirement_block_from(offshoot.config["file_paths"]["libraries"])

    requirement_blocks = TestPlugin._extract_plugin_requirement_blocks_from(offshoot.config["file_paths"]["libraries"])

    assert "TestPlugin Requirements" not in requirement_blocks
    assert "TestInvalidPlugin Requirements" in requirement_blocks

    TestInvalidPlugin._remove_plugin_requirement_block_from(offshoot.config["file_paths"]["libraries"])

    requirement_blocks = TestPlugin._extract_plugin_requirement_blocks_from(offshoot.config["file_paths"]["libraries"])

    assert "TestPlugin Requirements" not in requirement_blocks
    assert "TestInvalidPlugin Requirements" not in requirement_blocks


def test_plugin_global_on_install_callback_should_be_called_after_a_successful_installation(mocker):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False

    mocker.spy(TestPlugin, "on_install")

    TestPlugin.install()

    assert TestPlugin.on_install.call_count == 1

    TestPlugin.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True


def test_plugin_global_on_uninstall_callback_should_be_called_after_a_successful_uninstallation(mocker):
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False

    mocker.spy(TestPlugin, "on_uninstall")

    TestPlugin.uninstall()

    assert TestPlugin.on_uninstall.call_count == 1

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True


def test_plugin_an_error_should_be_raised_if_a_plugin_dependency_is_not_installed():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    with pytest.raises(offshoot.PluginError):
        TestPlugin2.install()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True


def test_plugin_should_pass_plugin_dependency_verification_if_all_dependencies_are_present():
    offshoot.config["allow"]["files"] = False
    offshoot.config["allow"]["config"] = False
    offshoot.config["allow"]["libraries"] = False
    offshoot.config["allow"]["callbacks"] = False

    TestPlugin.install()
    TestPlugin2.install()

    TestPlugin.uninstall()
    TestPlugin2.uninstall()

    offshoot.config["allow"]["files"] = True
    offshoot.config["allow"]["config"] = True
    offshoot.config["allow"]["libraries"] = True
    offshoot.config["allow"]["callbacks"] = True

def test_teardown():
    os.remove("plugins")
    os.remove("config")
    os.remove("libraries")

    if os.path.isfile("offshoot.manifest.json"):
        os.remove("offshoot.manifest.json")

    if os.path.isfile("requirements.plugins.txt"):
        os.remove("requirements.plugins.txt")
