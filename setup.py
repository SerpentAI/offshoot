#!/usr/bin/env python
from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = ""

packages = [
    'offshoot'
]

requires = [
    'PyYaml'
]

setup(
    name='offshoot',
    version="0.1.0",
    description='Dead simple plugin engine for files, config keys and packages. Supports: installation/uninstallation, callbacks, auto-imports & optional magic class annotations for protocol validation',
    long_description=long_description,
    author="Nicholas Brochu",
    author_email='nicholas@serpent.ai',
    packages=packages,
    include_package_data=True,
    install_requires=requires,
    entry_points={
        'console_scripts': ['offshoot = offshoot.main:execute']
    },
    license='Apache License v2',
    url='https://github.com/SerpentAI/offshoot',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5'
        'Programming Language :: Python :: 3.6'
    ]
)
