'''
Starting the configurator
'''

# System imports
import argparse
# 3rd party imports
import yaml

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
configurator = Configurator(config)
configurator.mainloop()
