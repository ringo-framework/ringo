#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'pyramid',
    'SQLAlchemy',
    'alembic',
    'transaction',
    'pyramid_tm<2.0',
    'pyramid_mako',
    'pyramid_beaker',
    'pyramid_mailer==0.14.1',
    'repoze.sendmail==4.1',
    'zope.sqlalchemy',
    'waitress',
    'babel',
    'formbar',
    'invoke',
    'dogpile.cache',
    'passlib',
    'python-dateutil',
    'fuzzy',
    'python-Levenshtein',
    'webhelpers',
    'psycopg2',
    'xlsxwriter'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ringo',
    version='1.16.2',
    description="Ringo is a small Python based high level web application framework build with Pyramid",
    long_description=readme + '\n\n' + history,
    author="Torsten Irländer",
    author_email='torsten.irlaender@googlemail.com',
    url='https://github.com/ringo-framework/ringo',
    packages=[
        'ringo',
    ],
    package_dir={'ringo':
                 'ringo'},
    entry_points={
        'paste.app_factory': [
            'main = ringo:main'
        ],
        'console_scripts': [
            'ringo=ringo.cli:main',
            'ringo-admin = ringo.scripts.admin:main'
        ],
        'babel.extractors': [
            'tableconfig = ringo.lib.i18n:extract_i18n_tableconfig'
            'formconfig = formbar.i18n:extract_i18n_formconfig'
        ],
        'pyramid.scaffold': [
            'ringo=ringo.scaffolds:BasicRingoTemplate'
            'ringo_extension=ringo.scaffolds:RingoExtensionTemplate'
        ]
    },
    message_extractors={
        'ringo': [
            ('**.py', 'python', None),
            ('templates/**.html', 'mako', None),
            ('templates/**.mako', 'mako', None),
            ('views/**.xml', 'formconfig', None),
            ('views/**.json', 'tableconfig', None),
            ('static/**', 'ignore', None)
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license='GNU General Public License v2 or later (GPLv2+)',
    zip_safe=False,
    keywords='ringo',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
