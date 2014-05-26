# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'alembic',
    'transaction',
    'pyramid_tm',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'pyramid_beaker',
    'pyramid_handlers',
    'pyramid_mailer',
    'zope.sqlalchemy',
    'waitress',
    'babel',
    'Sphinx',
    'formbar>=0.7',
    'invoke',
    'dogpile.cache',
    'behave',
    'coverage',
    'webtest',
    'mock',
    'py3o.template',
    'passlib'
]

tests_requires = [
]

setup(name='ringo',
      version='0.14.0',
      description='A simple web framework with base functionality to build web applications.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Torsten Irländer',
      author_email='torsten@irlaender.de',
      url='https://bitbucket.org/ti/ringo',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      #test_suite='ringo',
      test_suite='nose.collector',
      install_requires=requires,
      tests_require=tests_requires,
      setup_requires=["hgtools", "nose"],
      entry_points="""\
      [paste.app_factory]
      main = ringo:main
      [console_scripts]
      add_ringo_modul = ringo.scripts.add_modul:main
      [babel.extractors]
      tableconfig = ringo.lib.i18n:extract_i18n_tableconfig
      formconfig = formbar.i18n:extract_i18n_formconfig
      [pyramid.scaffold]
      ringo=ringo.scaffolds:BasicRingoTemplate
      """,
      message_extractors = {'ringo': [
            ('**.py', 'python', None),
            ('templates/**.html', 'mako', None),
            ('templates/**.mako', 'mako', None),
            ('views/**.xml', 'formconfig', None),
            ('views/**.json', 'tableconfig', None),
            ('static/**', 'ignore', None)]},
      )
