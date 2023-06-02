'''
Starting the configurator
'''

# System imports
import argparse
# 3rd party imports
import yaml
from pathlib import Path

# local imports
from CoBaIR.configurator import Configurator
from CoBaIR.bayes_net import load_config


# end file header
__author__ = 'Adrian Lubitz'

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str,
                    help='Path to a config file to load upon start.')
args = parser.parse_args()

# get file from args
config_path = args.file
if config_path:
    config = load_config(config_path)
else:
    config = None

configurator = Configurator(config=config)
# TODO: this is slightly complicated - could be solved if the configurator can distinguish between String/Path and dict and behaves accordingly.
if config_path:
    configurator.current_file_name = Path(args.file).absolute()
configurator.title_update()

configurator.app.exec_()