from setuptools import setup
from setuptools import find_packages
import bayesian_intention_recognition

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# TODO: if not TAG in pipeline given - then tage the tag
version = bayesian_intention_recognition.__version__

setup(name='CoBaBaIR',
      version=version,
      description='CoBaBaIR is a python lib for Context Based Bayesian Intention Recognition',
      author='Adrian Lubitz',
      author_email='Adrian.Lubitz@dfki.de',
      license='',
      install_requires=requirements,
      packages=find_packages())
