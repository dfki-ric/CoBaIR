"""installer for CoBaIR, the package metadata is in pyproject.toml."""

# System imports
import os
from setuptools import setup
# 3rd party imports

# local imports

# end file header
__author__ = 'Adrian Lubitz'


# use the tag as version when building in a GitHub Actions tag pipeline
if os.environ.get('GITHUB_REF_TYPE') == 'tag':
    VERSION = os.environ['GITHUB_REF_NAME']
else:
    VERSION = '0.0.0'

setup(version=VERSION)
