from setuptools import setup
from setuptools import find_packages
import CoBaBIR

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# TODO: if TAG in pipeline given use tag
version = CoBaBIR.__version__

setup(name='CoBaBIR',
      version=version,
      description='CoBaBIR is a python lib for Context Based Bayesian Intention Recognition',
      author='Adrian Lubitz',
      author_email='Adrian.Lubitz@dfki.de',
      license='',
      install_requires=requirements,
      packages=find_packages())
