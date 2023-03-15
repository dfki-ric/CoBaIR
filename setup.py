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

setup(name='CoBaIR',
      version=VERSION,
      description='CoBaIR is a python lib for Context Based Intention Recognition',
      author='Adrian Lubitz',
      author_email='Adrian.Lubitz@dfki.de',
      license='',
      install_requires=requirements,
      packages=find_packages())
