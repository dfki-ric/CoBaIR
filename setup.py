from setuptools import setup
from setuptools import find_packages
import CoBaIR

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# TODO: if TAG in pipeline given use tag
version = CoBaIR.__version__

setup(name='CoBaIR',
      version=version,
      description='CoBaIR is a python lib for Context Based Intention Recognition',
      author='Adrian Lubitz',
      author_email='Adrian.Lubitz@dfki.de',
      license='',
      install_requires=requirements,
      packages=find_packages())
