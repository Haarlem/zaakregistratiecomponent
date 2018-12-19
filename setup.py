#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

import setuptools.command.test

NAME = 'zaakmagazijn'

# -*- Classifiers -*-

classes = """
    Development Status :: 4 - Beta
    License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
    Topic :: Communications
    Topic :: Software Development :: Libraries :: Python Modules
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


# -*- Installation Requires -*-


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req, deps):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*path.split('/'))
    if (deps and not req.startswith('-e')) or (not deps and req.startswith('-e')):
        return []
    return [req]


def _reqs(*f, deps):
    return [
        _pip_requirement(r, deps) for r in (
            strip_comments(l) for l in open(
                os.path.join(os.getcwd(), 'requirements', *f)).readlines()
        ) if r]


def reqs(*f, deps=False):
    return [req for subreq in _reqs(*f, deps=deps) for req in subreq]

def deps(*f):
    return reqs(*f, deps=True)

print(reqs('base.txt'))
print(deps('base.txt'))


# -*- Long Description -*-

if os.path.exists('README.rst'):
    long_description = codecs.open('README.rst', 'r', 'utf-8').read()
else:
    long_description = 'See: https://github.com/haarlem/zaakregistratiecomponent'

# -*- %%% -*-

setuptools.setup(
    name=NAME,
    # packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version='0.9.14',
    description='Implementatie van het referentiecomponent Zaaksysteem (ZS)',
    long_description=long_description,
    keywords='zaaksysteem zakenmagazijn zds zaakservices documentservices soap zds',
    author='Maykin Media B.V.',
    platforms=['any'],
    license='EUPL 1.2',
    classifiers=classifiers,
    install_requires=reqs('base.txt'),
    tests_require=reqs('test.txt'),
    dependency_links=deps('base.txt'),
    zip_safe=False,
    include_package_data=True,
)
