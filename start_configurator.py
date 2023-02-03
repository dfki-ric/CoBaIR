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
from PyQt5 import QtWidgets, uic
import sys

# end file header
__author__ = 'Adrian Lubitz'

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str,
                    help='Path to a config file to load upon start.')
args = parser.parse_args()

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('configpyqt5.ui', self) # Load the .ui file
        self.show() # Show the GUI
        
# get file from args
# config_path = args.file
# if config_path:
#     config = load_config(config_path)
# else:
#     config = None
# configurator = Configurator(config)
# configurator.mainloop()

app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
app.exec_() # Start the application