#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGES.rst') as changes_file:
    changes = changes_file.read()

requirements = [line.strip() for line in open('requirements.txt')]

# setup_requirements = ['pytest-runner', ]

# test_requirements = ['pytest', ]

setup(
    author="Nils Hempelmann",
    author_email='info@nilshempelmann.de',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Utilities common to multiple WPS birds.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + changes,
    include_package_data=True,
    keywords='eggshell',
    name='eggshell',
    packages=find_packages(include=['eggshell']),
    # setup_requires=setup_requirements,
    # test_suite='tests',
    # tests_require=test_requirements,
    url='https://github.com/bird-house/eggshell',
    version='0.4.0',
    zip_safe=False,
)
