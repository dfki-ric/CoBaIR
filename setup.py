'''
installer for CoBaIR
'''

# System imports
import os
from setuptools import setup, find_packages
# 3rd party imports

# local imports

# end file header
__author__ = 'Adrian Lubitz'


# use the tag as version when building in a GitHub Actions tag pipeline
if os.environ.get('GITHUB_REF_TYPE') == 'tag':
    VERSION = os.environ['GITHUB_REF_NAME']
else:
    VERSION = '0.0.0'

with open('requirements/requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()


def read(fname: str) -> str:
    """Read the contents of a file and return it as a string."""
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


setup(
    name='cobair',
    version=VERSION,
    description='CoBaIR is a Python library for Context Based Intention Recognition',
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
    python_requires='>=3.8',
)
