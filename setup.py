import os

from setuptools import setup, find_packages

version = __import__('eggshell').__version__
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

reqs = [line.strip() for line in open('requirements.txt')]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
]

setup(name='eggshell',
      version=version,
      description='General utilities to write processes for climate data analysis.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=classifiers,
      author='David Huard',
      author_email='huard.david@ouranos.ca',
      url='http://eggshell.readthedocs.io/en/latest/',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      keywords='wps flyingpigeon pywps ipsl birdhouse conda climate indices species',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='eggshell',
      install_requires=reqs,
      )
