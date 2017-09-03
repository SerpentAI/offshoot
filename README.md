# offshoot

This one day in the past, you took your first step on your programming journey. Some days were tough, some days were great. You made progress. You made mistakes. You learned some best practices and design patterns. You've come to idolize low coupling and modularity. Eventually, you started working on more ambitious projects, always increasing in complexity; the possibilities endless. After implementing your 7th export format for your latest project, the words of the great Raymond Hettinger come to mind: _There's got to be a better way!_ After a short stint going all out on inheritance and mixins, you turn your attention to plugins. You read up on them, get the general idea and start looking at what's available for Python. You are happy to find out there are a quite a few on the market. You start trying them out and for the most part, they work great, but it always feels like something is missing. Perhaps they make you go through crazy code gymnastics, lack features or are plain just horrible to look at. This is the moment you discover _offshoot_.

***offshoot***:

* Is a modern, elegant and minimalistic plugin system for Python 3.5+
* Is unintrusive; Stays out of our way. No file copying, no symlinks, nada!
* Provides a clear and simple plugin definition format.
* Understands your flow: Provides installation callbacks, can maintain a configuration and/or a requirements file for your plugins and has an optional plugin validation system on install.
* Can discover and import any plugin of any type anywhere in your code with a one-liner. No more complex plugin management.
* Batteries included. Comes with an executable to install/uninstall plugins.
* Is fully-tested and is under active development.
* Does not aim to please the _PEP 8_ gods and the purists. Some dark magic is used unapologetically.

## Quick Tour

**Your Class you'd like to make pluggable**

```python
class ExportFormat:
	def __init__(self):
    	self.name = "Export Format"

    def export(self, data):
    	raise NotImplementedError()

    @classmethod
    def is_an_export_format(cls):
    	return True
```

**Your Class made pluggable with _offshoot_**
```python
import offshoot

class ExportFormat(offshoot.Pluggable):
	def __init__(self):
    	self.name = "Export Format"

    @offshoot.expected
    def export(self, data):
    	raise NotImplementedError()

    @classmethod
    @offshoot.forbidden
    def is_an_export_format(cls):
    	return True
```
Yes, that's it! More about those optional decorators later.

**A sample _offshoot_ plugin definition**
```python
import offshoot

class YAMLExportFormatPlugin(offshoot.Plugin):
    name = "YAMLExportFormatPlugin"
    version = "0.1.0"

    libraries = ["PyYAML"]

    files = [
        {"path": "export_formats/yaml.py", "pluggable": "ExportFormat"}
    ]

    config = {
        "export_options": {
        	"width": 80
        }
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)

if __name__ == "__main__":
    offshoot.executable_hook(YAMLExportFormatPlugin)
```

**A sample _offshoot_ plugin file**
```python
import offshoot
from export_format import ExportFormat

import yaml

class YAMLExportFormat(ExportFormat):
	def export(self, data):
    	return yaml.dump(data)
```

**Installing an _offshoot_ plugin from the command line**

`offshoot install YAMLExportFormatPlugin`

**Automatic _offshoot_ plugin discovery and importing**
```python
import offshoot
offshoot.discover("ExportFormat", globals())

YAMLExportFormat # Now in scope!
```

**Verifying if class name string maps to a discovered plugin class**
```python
import offshoot
class_mapping = offshoot.discover("ExportFormat")  # We omit scope param to get the class mapping

"YAMLExportFormat" in class_mapping  # True
```

## Requirements

* PyYAML (On the roadmap to make it optional so the project is 100% dependency-free!)

## Installation

`pip install offshoot`

## Configuration

### Default Configuration Values
```python
{
    "modules": [],
    "file_paths": {
        "plugins": "plugins",
        "config": "config/config.plugins.yml",
        "libraries": "requirements.plugins.txt"
    },
    "allow": {
    	"plugins": True,
        "files": True,
        "config": True,
        "libraries": True,
        "callbacks": True
    },
    "sandbox_configuration_keys": True
}
```

### Initializing offshoot

Initializing _offshoot_ will save a YAML copy of the default configuration to _offshoot.yml_ which you can then modify to suit your needs. Just run the following in the command line: `offshoot init`

### Configuration Keys

* **modules**: Perhaps the most important key to modify since nothing will happen without some valid module paths in there. _offshoot_ needs to discover pluggable classes in the project at import time. It will explore the modules listed here to find classes that extend _offshoot.Pluggable_
* **file_paths**: Directories and file paths to use when _offshoot_ needs to hit the file system. _plugins_ is where _offshoot_ will look for plugin files. The defaults should suffice, but do make sure they exist.
* **allow**: _offshoot_ allows you to enable/disable certain part of the plugin installation. It is recommended to leave all values to True.
* **sandbox_configuration_keys**: If you chose to let _offshoot_ merge configuration keys during plugin installation, it can either merge them all at the root level (False) or sandbox them under the plugin name (True)

## Usage

### Initializing Offshoot

The first thing you will want to do after installing _offshoot_ is run `offshoot init` in the command line at the root of your project. This will create a configuration file named _offshoot.yml_. You can leave it be for now but we will go back to it later.

### Making Your Classes Pluggable

To make a class pluggable with _offshoot_ all that technically needs to be done is extend it with _offshoot.Pluggable_

So you go from this:
```python
class Shape:
	pass
```

To this:
```python
import offshoot

class Shape(offshoot.Pluggable):
	pass
```

Then for every class you make pluggable, you append its module path to _offshoot.yml_ under the modules key. This means that if you make `shape.py` and `shapes/rectangle.py` pluggable, your modules value will look like this `modules: ["shape", "shapes/rectangle"]`

#### Magic Validation

_offshoot_ comes with an optional validation system for your pluggable classes. You can control which class, instance and static methods are either _expected_, _accepted_ or _forbidden_ in a plugin file. The way you do this couldn't be any simpler: you wrap them with a decorator. It ends up looking like the following:

```python
import offshoot

class PluggableClass(offshoot.Pluggable):
    @offshoot.expected
    def expected_function(self):
        raise NotImplementedError()

    @classmethod
    @offshoot.accepted
    def accepted_function(cls):
        raise NotImplementedError()

    @staticmethod
    @offshoot.forbidden
    def forbidden_function():
        raise NotImplementedError()
```
If a plugin file is missing an _expected_ method, or defining a _forbidden_ method, it will be rejected and the installation will be stopped and reverted.

They are called magic decorator because under the hood, they do absolutely nothing. They are however found using Python's abstract syntax trees (_ast_ in the stdlib) during plugin installation and validation can be performed.

#### Installation Callbacks

In addition to magic validators, you have the option to add callbacks that will be executed for each file installed/uninstalled by a plugin.

To leverage these callbacks, simply add these functions to your pluggable class:

```python
@classmethod
def on_file_install(cls, **kwargs):
	pass

@classmethod
def on_file_uninstall(cls, **kwargs):
    pass
```

Contained in `kwargs` are the file path and the name of the pluggable class.

One common application for these callbacks would be to seed some values in a database. If we stick the ExportFormat example, once you install a YAMLExportFormat plugin, you may want to add it to a _export_formats_ table along with the name of the class. That could then allow list the available export format options in a more logical fashion. Similarly, you'd want that option to be cleaned up when you uninstall the plugin.

### Anatomy of an _offshoot_ Plugin

#### Expected File Structure

```sh
PLUGINS_DIRECTORY (defined in offshoot.yml)
├── ShapesPlugin  # Name of the plugin. Matches the plugin class name in plugin.py
│   ├── __init__.py
│   ├── files  # Any file other than the plugin definition goes here
│   │   ├── __init__.py
│   │   ├── helpers.py  # Supporting file. Not in plugin definition but can be accessed by plugin files.
│   │   └── shapes
│   │       ├── __init__.py
│   │       ├── rectangle.py  # Variant of the Shape pluggable class. Included in plugin definition file
│   │       ├── star.py  # Variant of the Shape pluggable class. Included in plugin definition file
│   │       └── triangle.py  # Variant of the Shape pluggable class. Included in plugin definition file
│   └── plugin.py  # Plugin definition file
├── __init__.py
```

You are free to structure your file hierarchy exactly the way you want inside of the _files_ directory. You can also add as many supporting files as needed.

`__init__.py` files DO need to be peppered everywhere as we want our plugin structure to be accessible as a package.


#### Plugin Definition File (plugin.py)

The plugin definition file turns out to be a Python file with a class that extends `offshoot.Plugin`. The name of that class needs to be an exact match of the name of the directory containing the plugin.

Here's what plugin definition file would look like for a plugin using the file structure above. It is annotated to explain what the various sections do.

```python
import offshoot

class ShapesPlugin(offshoot.Plugin):  # We extend offshoot.Plugin
    name = "ShapesPlugin"  # We define a name for the plugin. Matches the class name.
    version = "0.1.0"  # We define a version number for the plugin.

    # A list of plugin dependencies to check for (by name) before installing the plugin.
    # Optional.
    plugins = [
    	"RequiredShapesPlugin"
    ]

    # A list of required PyPI packages for the plugin.
    # Optional. These libraries will be merge to your offshoot requirements.txt during the installation. Set to None if you don't intend to use it.
    libraries = [
        "requests",
        "requests-respectful==0.2.0"
    ]

    # A list of file objects that target pluggable classes in the project.
    # Required. "path" is the file path relative to the plugin root. "pluggable" is the pluggable class' name.
    files = [
        {"path": "shapes/rectangle.py", "pluggable": "Shape"},
        {"path": "shapes/triangle.py", "pluggable": "Shape"},
        {"path": "shapes/star.py", "pluggable": "Shape"}
    ]

    # A Python dict containing configuration keys that can be referenced by your plugin files at runtime.
    # Optional. Any valid Python dict is accepted. Set to None if you don't intend to use it.
    config = {
        "i_am_a": {
            "plugin": True,
            "human": False
        },
        "urls": ["http://serpent.ai", "https://github.com/SerpentAI/offshoot"],
        "count": 42,
    }

    # Callbacks to be performed once per install / uninstall
    # Optional.
    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)

# This hook always needs to be present in a plugin definition file.
# It is used by the installation process. Pass it the class you just defined above.
if __name__ == "__main__":
    offshoot.executable_hook(ShapesPlugin)
```

#### Plugin Files Extending the Pluggable Classes

Each plugin file needs to define a class that extends one of the classes that were previously made pluggable. If magic validation decorators were used when making the class pluggable, the plugin file needs to validate against that protocol successfully to be installed.

Here is a sample plugin file, following our Shapes plugin theme:

```python
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
```

You are free to go way beyond the pluggable class' protocol. You can require functions from supporting files bundled with the plugin and make use of your required PyPI packages and/or configuration keys.

### The _offshoot_ Manifest

The _offshoot_ manifest is a critical file that gets created when you attempt to install a plugin for the first time. It contains the metadata of installed plugins and helps maintain the overall _offshoot_ state. Look for _offshoot.manifest.json_ if you want to take a peek under the hood. Be aware that editing or deleting this file will cause issues!

### The _offshoot_ Executable

The executable is rather minimalistic at the moment but it used to perform two crucial operations: Installing and uninstalling plugins.

#### Installing Plugins

The first step is making sure the plugin has been copied/cloned into the plugin directory defined in _offshoot.yml_

After that, simply run the following in the command line:

`offshoot install PLUGIN_NAME`

**What happens when a plugin is installed?**

1. The _offshoot_ configuration file is consulted to fetch the allow flags
2. If _plugins_ are allowed: Every plugin listed as a dependency in the plugin definition is verified to be installed before continuing.
3. If _files_ are allowed: Every plugin file in the plugin definition is validated against its pluggable class' protocol. If even one validation test fails, the installation fails and is reverted. File installation callbacks are executed.
4. If _config_ is allowed: The configuration keys contained in the plugin definition file are merged in the configuration file defined in _offshoot.yml_.
5. If _libraries_ are allowed: Libraries contained in the plugin definition file are merged in the libraries file defined in _offshoot.yml_.
6. If _callbacks_ are allowed: The _on_install_ callback is executed.
7. The plugin metadata is appended to the manifest.

The installation process will not automatically install libraries with _pip_. It is assumed the user will permorm the pip installation.

#### Uninstalling Plugins

`offshoot uninstall PLUGIN_NAME`


### Discovering & Importing Plugins

Last but not least, a simple way of getting installed plugins' classes into scope has been provided.

Here's how it's done:

```python
import offshoot
offshoot.discover("Shape", globals())

# All installed plugin classes that extend the Shape pluggable class are now into scope!
```

This can be done literally anywhere in your application.

### Tips & Tricks

#### Listing installed plugins

A utility method is exposed allowing you to fetch a list of the currently installed plugins as per the manifest.

Simply run:
```python
offshoot.installed_plugins()
```

Example output:
```python
["ShapesPlugin - 0.1.0"]
```

#### Merging the _offshoot_ configuration keys with your application configuration at runtime.

Chances are you already have a YAML configuration file for your application. In some situations, it may become desirable to merge that configuration dict with _offshoot_'s configuration dict.

Here's a code snippet to achieve this:

```python
import yaml

# Application Configuration
with open("config/config.yml", "r") as f:
    config = yaml.safe_load(f)

# Offshoot Configuration
import offshoot

with open(offshoot.config["file_paths"]["config"], "r") as f:
    plugin_config = yaml.safe_load(f)

# Merge Configuration. Application Configuration takes priority in the key space.
config = {**plugin_config, **config}
```

You can then import _config_ from this file to have the merged configurations.

## Tests

Unit tests for the project can be run with the following command:

`python -m pytest tests --spec`

You can install the test requirements by refering to _requirements.test.txt_ in the repository.


## Examples

You can find full examples in the `examples` directory of the repository.

## Roadmap / Contribution Ideas

* Make PyYaml optional. Use it if it's there, otherwise default on JSON or INI
* Explore supporting the extension of 3rd-party modules.
* Windows support? Python 2 branch?
* Clean up tests. A lot of repetition.
* ... Anything else that makes sense really!

_If you like offshoot, feel free to check out [requests-respectful](https://github.com/SerpentAI/requests-respectful), also by [SerpentAI](http://serpent.ai)_