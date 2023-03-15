from setuptools import setup
from setuptools import find_packages
import CoBaIR
import os

with open('requirements/requirements.txt') as f:
    requirements = f.read().splitlines()

# TODO: if TAG in pipeline given use tag
if 'CI_COMMIT_TAG' in os.environ:
    VERSION = os.environ['CI_COMMIT_TAG']
else:
    VERSION = '0.0.0'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='CoBaIR',
      version=VERSION,
      description='CoBaIR is a python lib for Context Based Intention Recognition',
      author='Adrian Lubitz',
      author_email='Adrian.Lubitz@dfki.de',
      license='BSD 3-Clause',
      keywords="intention recognition context human machine interaction robot bayesian",
      url="https://github.com/dfki-ric/CoBaIR",
      install_requires=requirements,
      packages=find_packages(),
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: X11 Applications :: Qt",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python :: 3.8",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
      ],
      python_requires='>=3.8')
