"""installer for CoBaIR, the package metadata is in pyproject.toml."""

# System imports
import os
from setuptools import setup
# 3rd party imports

# local imports

# end file header
__author__ = 'Adrian Lubitz'


# use the release tag (5.0.0 or v5.0.0) as version when building in a GitHub Actions release
if os.environ.get('GITHUB_REF_TYPE') == 'tag':
    VERSION = os.environ['GITHUB_REF_NAME'].removeprefix('v')
else:
    VERSION = '0.0.0'

setup(version=VERSION)
