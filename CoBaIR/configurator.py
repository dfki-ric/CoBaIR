'''
This module is a GUI configurator to create configurations for context based intention recognition - it can as well be used in a live mode to test the configuration
'''

# System imports
import sys
import os
from collections import defaultdict
from copy import deepcopy
from types import FunctionType as function
from pathlib import Path
import itertools
import argparse
# 3rd party imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyqtgraph as pg
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QPushButton,\
    QFrame, QGridLayout, QSizePolicy, QSlider, QFileDialog, QMessageBox

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont, QFontMetrics, QLinearGradient, QColor

import yaml
import numpy as np
import logging
# local imports
from .bayes_net import BayesNet, load_config
import webbrowser

# end file header
__author__ = 'Adrian Lubitz'


class NewIntentionDialog(QDialog):
    """Dialog Window for new Intention"""

    def __init__(self, parent=None, intention: str = None) -> None:
        """
        Extends the Constructor of Dialog to use an already existing intention.

        If an intention is given it will be filled in the corresponding text field.

        Args:
            intention: An intention that will be filled in the dialog
        """
        dialog = QDialog()
        dialog.deleteLater()
        self.intention = intention
        super().__init__(parent)
        self.result = None
        self.setModal(True)
        self.body()
        self.show()

    def body(self):
        """
        Sets the Layout.

        Args:
            master: the master window this dialog belongs to
        Returns:
            tk.Entry:
                the initial focus
        """
        uic.loadUi(Path(Path(__file__).parent, 'NewIntention.ui'), self)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red")
        if self.intention:
            self.intention_entry.setText(self.intention)
        return self.intention_entry  # initial focus

    def get_result(self):
        """
        Applies the result to hand it over to the master
        """
        self.error_label.setText("")
        result = self.intention_entry.text().strip()
        if not result:
            self.error_label.setText("Intentions cannot be empty")
        else:
            self.accept()
        return result


class NewCombinedContextDialog(QDialog):
    """Dialog Window for new combined Context influence"""

    def __init__(self, parent=None, intentions: dict = None) -> None:
        """
        Extends the Constructor of Dialog to make config available.

        Args:
            intentions:
                The intentions part of the config
                Example:
                    {hand over tool:
                        human activity:
                            idle: 4
                            working: 1
                        speech commands:
                            handover: 5
                            other: 0
                            pickup: 0
                    pick up tool:
                        speech commands:
                            handover: 0
                            other: 0
                            pickup: 5
                        ? !!python/tuple
                        - speech commands
                        - human activity
                            : ? !!python/tuple
                            - pickup
                            - working
                                : 5
                        human activity:
                            idle: 4
                            working: 3
                    }
        """
        self.intentions = deepcopy(intentions)
        self.original_instantiations = defaultdict(dict)
        super().__init__(parent)
        self.result = None
        self.body()
        self.show()

    def body(self):
        """
        Sets the Layout.

        Args:
            master: the master window this dialog belongs to
        """
        uic.loadUi(Path(Path(__file__).parent,
                   'NewCombinedContextInfluence.ui'), self)

        values = list(self.intentions.keys())

        self.intention_selection.addItems(values)
        self.intention_selection.setCurrentIndex(0)
        # Button
        self.additional_context.clicked.connect(self.new_instantiation)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red")
        # contexts
        self.contexts = {}
        self.grid_layout = QGridLayout()
        self.context_frame.setLayout(self.grid_layout)
        for context, instantiations in list(self.intentions.values())[0].items():
            if not isinstance(context, tuple):
                self.contexts[context] = instantiations
        self.context_selections = []
        self.context_menus = []
        self.instantiation_selections = []
        self.instantiation_menus = []
        for _ in range(2):
            self.new_instantiation()

    def context_selected(self, context: str, i: int):
        """
        Callback for context selection in dropdown

        Args:
            context: A context name
            i: the position of the dropdown menu
        """
        self.instantiation_menus[i].setVisible(False)
        self.instantiation_menus[i].deleteLater()

        for inst in self.contexts[context]:
            self.original_instantiations[context][str(inst)] = inst

        instantiations = list(self.original_instantiations[context].keys())
        instantiations = list(map(str, instantiations))

        self.instantiation_selections[i] = QComboBox(self.context_frame)
        self.instantiation_selections[i].clear()
        self.instantiation_selections[i].addItems(instantiations)
        self.instantiation_selections[i].setCurrentText(
            self.instantiation_selections[i].currentText())

        self.grid_layout.addWidget(self.instantiation_selections[i], i+1, 1)

        self.instantiation_selections[i].setCurrentText(
            str(list(self.contexts[context].keys())[0]))

        # available context -> every dropdown should only have available + selected
        available_context = self._eval_available_context()
        for i_m, menu in enumerate(self.context_menus):
            menu.setVisible(False)
            menu.deleteLater()
            contexts = [self.context_selections[i_m].currentText()] + \
                available_context
            self.context_selections[i_m] = QComboBox(self.context_frame)
            self.context_selections[i_m].addItems(contexts)
            self.context_selections[i_m].setCurrentText(
                self.context_selections[i_m].currentText())
            self.context_selections[i_m].currentTextChanged.connect(
                lambda text, i=i_m: self.context_selected(text, i))
            self.grid_layout.addWidget(self.context_selections[i_m], i_m+1, 0)

    def _eval_available_context(self):
        """
        evaluate which contexts are available for the dropdown

        Returns:
            list:
                A list of available contexts
        """
        available_context = list(self.contexts.keys())
        for selection in self.context_selections:
            available_context.remove(selection.currentText())
        return available_context

    def new_instantiation(self):
        """
        Creates new Entries to input more context instantiations
        """
        available_context = self._eval_available_context()
        i = len(self.context_selections)
        if not available_context:
            self.error_label.setText('No more context available')
            return
        self.context_selections.append(QComboBox(self.context_frame))
        self.context_selections[-1].addItems(available_context)
        self.context_selections[-1].setCurrentIndex(0)
        self.context_selections[-1].currentTextChanged.connect(
            lambda text, i=i: self.context_selected(text, i))
        self.context_menus.append(self.context_selections[-1])
        self.grid_layout.addWidget(self.context_menus[-1], i+1, 0)

        instantiations = list(self.contexts[available_context[0]].keys())
        instantiations = list(map(str, instantiations))
        self.instantiation_selections.append(QComboBox(self.context_frame))
        self.instantiation_selections[-1].addItems(instantiations)
        self.instantiation_selections[-1].setCurrentIndex(0)
        self.instantiation_menus.append(self.instantiation_selections[-1])
        self.grid_layout.addWidget(self.instantiation_menus[-1], i+1, 1)

        self.context_selected(self.context_selections[-1].currentText(), i)

    def get_result(self):
        """
        Applies the result to hand it over to the master
        """
        intention = self.intention_selection.currentText()
        value = self.value_selection.currentText()
        contexts = []
        instantiations = []
        for i, context_selection in enumerate(self.context_selections):
            contexts.append(context_selection.currentText())
            instantiations.append(
                self.original_instantiations[
                    context_selection.currentText()
                ][
                    self.instantiation_selections[i].currentText()
                ])
        # intention: str, contexts: tuple, instantiations: tuple, value: int
        result = {'intention': intention, 'value': int(value), 'contexts': tuple(
            contexts), 'instantiations': tuple(instantiations)}
        self.accept()
        return result


class NewContextDialog(QDialog):
    """Dialog Window for new Context"""

    def __init__(self, parent=None, predefined_context: dict = None) -> None:
        """
        Extends the Constructor of Dialog to use already existing context and 
            the corresponding instantiations and values.

        If context and their corresponding instantiations and values are given 
            it will be filled in the corresponding text fields.

        Args:
            predefined_context:
                Context with the corresponding instantiations.
                Example: {'speech commands': {
                    'pickup': 0.2, 'handover': 0.2, 'other': 0.6}}
        """
        dialog = QDialog()
        dialog.deleteLater()
        self.predefined_context = deepcopy(predefined_context)
        super().__init__(parent)
        self.result = None
        self.setModal(True)
        self.body()
        self.show()

    def body(self):
        """
        Sets the Layout.

        Args:
            master: the master window this dialog belongs to
        Returns:
            tk.Entry:
                the initial focus
        """
        uic.loadUi(Path(Path(__file__).parent, 'NewContext.ui'), self)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red")
        self.instantiations = []
        self.shown_instantiations = 0
        self.grid_layout = QGridLayout()
        self.instantiations_frame.setLayout(self.grid_layout)
        self.instantiations_frame.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        # TODO: Fill the entries here if predefined_context is given!
        if self.predefined_context:
            # it's always only one new context
            context = list(self.predefined_context.keys())[0]
            instantiations = self.predefined_context[context]
            self.context_entry.setText(context)
        else:
            instantiations = {}
        while(self.shown_instantiations < 2 or instantiations):

            name_entry = QLineEdit()
            probability_entry = QLineEdit()
            remove_button = QPushButton('-')
            remove_button.clicked.connect(
                lambda _, btn=remove_button: self.remove_instantiation(btn))
            if instantiations:
                # get name
                name = list(instantiations.keys())[0]
                # get value
                value = instantiations[name]
                # set entries
                name_entry.setText(str(name))
                probability_entry.setText(str(value))
                # del entry
                del instantiations[name]
            self.grid_layout.addWidget(
                name_entry, self.shown_instantiations+1, 0)
            self.grid_layout.addWidget(
                probability_entry, self.shown_instantiations+1, 1)
            self.grid_layout.addWidget(
                remove_button, self.shown_instantiations+1, 2)
            self.instantiations.append(
                (name_entry, probability_entry, remove_button))
            self.shown_instantiations += 1
        self.more.clicked.connect(self.new_instantiation)
        return self.context_entry

    def remove_instantiation(self, remove_button):
        """
        Callback for the remove_button
        Args:
            remove_button: the remove_button clicked
        """
        # find the index of the row containing the remove_button
        self.error_label.setText("")
        index = -1
        for i, (_, _, btn) in enumerate(self.instantiations):
            if btn is remove_button:
                index = i
                break
        if index != -1:
            # remove the row from the layout and from the instantiations list
            name_entry, probability_entry, _ = self.instantiations.pop(index)
            self.grid_layout.removeWidget(name_entry)
            self.grid_layout.removeWidget(probability_entry)
            self.grid_layout.removeWidget(remove_button)
            name_entry.deleteLater()
            probability_entry.deleteLater()
            remove_button.deleteLater()
            self.shown_instantiations -= 1
        self.grid_layout.update()

    def new_instantiation(self):
        """
        Creates two new Entries to input more instantiations
        """
        name_entry = QLineEdit(self.instantiations_frame)
        probability_entry = QLineEdit(self.instantiations_frame)
        remove_button = QPushButton('-', self.instantiations_frame)
        remove_button.clicked.connect(
            lambda _, btn=remove_button: self.remove_instantiation(btn))
        self.instantiations.append(
            (name_entry, probability_entry, remove_button))
        row_count = self.grid_layout.rowCount()
        self.grid_layout.addWidget(name_entry, row_count, 0)
        self.grid_layout.addWidget(probability_entry, row_count, 1)
        self.grid_layout.addWidget(remove_button, row_count, 2)
        self.shown_instantiations += 1
        self.grid_layout.update()
        # Raise ValueError if both name_entry and probability_entry are empty
        if not name_entry.text() and not probability_entry.text():
            self.error_label.setText(
                "Both name and probability cannot be empty.")
        elif not name_entry.text():
            self.error_label.setText("Name cannot be empty.")
        elif not probability_entry.text():
            self.error_label.setText("Probability cannot be empty.")

    def get_result(self):
        """
        Get the result of the New Context dialog.
        """
        result = defaultdict(lambda: defaultdict(dict))
        errors = []
        context_entry = self.context_entry.text().strip()
        if not context_entry:
            errors.append("Context cannot be empty.")
        else:
            for i, instantiation in enumerate(self.instantiations):
                key = instantiation[0].text().strip()
                value = instantiation[1].text().strip()
                if not key and not value:
                    errors.append(
                        f"Name and probability cannot be empty in row {i+1}.")
                elif not key:
                    errors.append(f"Name cannot be empty in row {i+1}.")
                elif not value:
                    errors.append(f"Probability cannot be empty in row {i+1}.")
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        errors.append(
                            f"Probability must be a number in row {i+1}.")
                    else:
                        result[self.context_entry.text().strip()][key] = value
        if errors:
            self.error_label.setText("\n".join(errors))
        else:
            self.accept()
        return result


class Configurator(QtWidgets.QMainWindow):
    '''
    GUI configurator to create configurations for context based intention recognition.
    It can as well be used in a live mode to test the configuration
    '''

    def __init__(self, *args, config: dict = None, **kwargs):
        '''
        Setting up the GUI

        Args:
            config: A dict with a config following the config format.
        '''
        self.app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        # self.figure = plt.figure()
        # self.canvas = FigureCanvas(self.figure)
        # creating a graph item
        # setting configuration options
        pg.setConfigOptions(antialias=True)
        # creating graphics layout widget
        self.win = pg.GraphicsLayoutWidget()
        # adding view box to the graphic layout widget
        self.view = self.win.addViewBox()
        self.graph_item = TwoLayerGraph()
        self.view.addItem(self.graph_item)
        self.setup_layout()
        self.bayesNet = BayesNet(config)
        self.create_fields()
        self.show()  # Show the GUI
        

    def create_fields(self):
        """
        Creates all necessary fields in the GUI.

        This should be used whenever the config is changed.
        It reads all values from the config and adjusts the GUI accordingly.
        """
        self.set_context_dropdown(self.bayesNet.config['contexts'].keys())

        self.set_influencing_context_dropdown(
            self.bayesNet.config['contexts'].keys())

        self.set_intention_dropdown(self.bayesNet.config['intentions'].keys())
        self.adjust_button_visibility()
        self.set_decision_threshold()
        self.set_context_dropdown(self.bayesNet.config['contexts'].keys())

        self.set_influencing_context_dropdown(
            self.bayesNet.config['contexts'].keys())

        self.set_intention_dropdown(self.bayesNet.config['intentions'].keys())
        self.adjust_button_visibility()
        self.set_decision_threshold()
        self.fill_advanced_table()
        self.draw_graph()
        self.original_config = deepcopy(self.bayesNet.config)

    def set_decision_threshold(self):
        """
        This sets value in the decision threshold entry from the config
        """
        self.decision_threshold_entry.setText(
            str(self.bayesNet.config['decision_threshold']))

    def adjust_button_visibility(self):
        """
        Adjusts if buttons are visible or not.

        Buttons for edit and delete will only be visible 
            if there is a corresponding intention or context already created.
        """
        if self.bayesNet.config['contexts']:
            # set visible
            self.edit_context_button.show()
            self.delete_context_button.show()
            self.grid_layout.addWidget(self.new_context_button, 0, 4)
        else:
            self.edit_context_button.hide()
            self.delete_context_button.hide()
            self.grid_layout.addWidget(self.new_context_button, 0, 2)
        if self.bayesNet.config['intentions']:
            # set visible
            self.edit_intention_button.show()
            self.delete_intention_button.show()
            self.grid_layout.addWidget(self.new_intention_button, 2, 6)
        else:
            self.edit_intention_button.hide()
            self.delete_intention_button.hide()
            self.grid_layout.addWidget(self.new_intention_button, 2, 4)

    def new_context(self):
        """
        Open a new Dialog to create new contexts.
        """
        # open small dialog to create context
        dialog = NewContextDialog(self)

        def update_and_close():
            self.error_label.setText("")
            result = dialog.get_result()
            if not result:
                self.error_label.setText(
                    "At least one instantiation is required.")
                return
            try:
                old_context_name = list(result.keys())[0]
                new_instantiations = result[old_context_name]
                if new_instantiations:
                    self.bayesNet.add_context(
                        old_context_name, new_instantiations)
            except AssertionError as error_message:
                self.error_label.setText(str(error_message))
            # update view!
            self.create_fields()
            self.context_selection.setCurrentText(old_context_name)
            # Explicit call is necessary because setCurrentText seems not to trigger the callback
            self.context_selected(old_context_name)
            dialog.accept()

        dialog.ok_button.setDefault(True)
        dialog.ok_button.clicked.connect(update_and_close)
        dialog.cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def edit_context(self):
        """
        Edit the currently selected context.

        !!! note
        Changing the name of an instantiation will always set the influence value 
            of this instantiation to zero for all intentions!

        !!! note
        The GUI can only handle strings for now. 
        This means every instantiation name will be casted to a string upon editing.
        """
        # TODO: renaming instantiations should not neccesarily put influence values to zero - check cases
        # TODO: this will always set the instantiations as Strings
        # Open the new Context dialog with prefilled values
        # open small dialog to create context

        context = self.context_selection.currentText()
        instantiations = self.bayesNet.config['contexts'][context]
        dialog = NewContextDialog(self, predefined_context={
            context: instantiations})

        def update_and_close():
            self.error_label.setText("")
            result = dialog.get_result()
            if not result:
                self.error_label.setText(
                    "At least one instantiation is required.")
                return
            try:
                old_context_name = list(result.keys())[0]
                new_instantiations = result[old_context_name]
                if new_instantiations:
                    self.bayesNet.edit_context(
                        context, new_instantiations, old_context_name)
            except (ValueError, AssertionError) as error_message:
                self.error_label.setText(str(error_message))
            self.create_fields()
            self.context_selection.setCurrentText(old_context_name)
            self.context_selected(old_context_name)
            dialog.accept()
        dialog.ok_button.setDefault(True)
        dialog.ok_button.clicked.connect(update_and_close)
        dialog.cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def delete_context(self):
        """"
        Deletes the currently selected context.
        """
        self.error_label.setText("")
        context = self.context_dropdown.currentText()
        try:
            self.bayesNet.del_context(context)
        except AssertionError as error_message:
            self.error_label.setText(str(error_message))
        self.create_fields()

    def new_intention(self):
        """
        Open a new Dialog to create new intentions.
        """
        dialog = NewIntentionDialog(self)

        def update_and_close():
            self.error_label.setText("")
            result = dialog.get_result()
            if not result:
                return
            if result:
                try:
                    self.bayesNet.add_intention(result)
                except AssertionError as error_message:
                    self.error_label.setText(str(error_message))
            # update view!
            self.create_fields()
            self.intention_dropdown.setCurrentText(result)
            # Explicit call is neccessary because set seems not to trigger the callback
            self.influencing_context_selected(result)
        dialog.ok_button.clicked.connect(update_and_close)
        dialog.cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def edit_intention(self):
        """
        Edit the name of the currently selected intention
        """
        # open small dialog to create context
        intention = self.intention_dropdown.currentText()
        dialog = NewIntentionDialog(self, intention=intention)

        def update_and_close():
            self.error_label.setText("")
            result = dialog.get_result()
            if not result:
                return
            if result:
                try:
                    self.bayesNet.edit_intention(intention, result)
                except ValueError as error_message:
                    self.error_label.setText(str(error_message))
            self.create_fields()
            self.intention_dropdown.setCurrentText(result)
            # Explicit call is necessary because set seems not to trigger the callback
            self.influencing_context_selected(result)
            dialog.accept()

        dialog.ok_button.setDefault(True)
        dialog.ok_button.clicked.connect(update_and_close)
        dialog.cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def delete_intention(self):
        """
        Delete the currently selected intention
        """
        self.error_label.setText("")
        intention = self.intention_dropdown.currentText()
        try:
            self.bayesNet.del_intention(intention)
        except AssertionError as error_message:
            self.error_label.setText(str(error_message))
        self.create_fields()

    def on_clicked_advanced(self):
        """
        Un/folds the advanced section
        """
        if self.advanced_folded:
            # Change text to up arrow
            self.advanced_label.setText("advanced \u25B2")
            self.advanced_folded = False
            self.advanced_hidden_frame.show()
            self.new_combined_influence_button.show()
        else:
            # Change text back to down arrow
            self.advanced_label.setText("advanced \u25BC")
            self.advanced_folded = True
            self.advanced_hidden_frame.hide()
            self.new_combined_influence_button.hide()

    def new_combined_influence(self):
        """
        Callback for the button
        """
        self.error_label.setText("")
        try:
            dialog = NewCombinedContextDialog(
                self, intentions=self.bayesNet.config['intentions'])
        except IndexError:
            self.error_label.setText(
                "Intentions and Contexts need to be defined before combining them")
            return
        except Exception as e:
            self.error_label.setText(str(e))
            return

        def update_and_close():
            result = dialog.get_result()
            try:
                self.bayesNet.add_combined_influence(
                    intention=result['intention'], contexts=result['contexts'], instantiations=result['instantiations'], value=result['value'])
            except ValueError as error_message:
                self.error_label.setText(str(error_message))
            self.create_fields()

        dialog.ok_button.clicked.connect(update_and_close)
        dialog.cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def fill_advanced_table(self):
        '''
        Fill the content of the table containing combined influence values
        '''

        font = QFont("Times New Roman", 13)
        self.advanced_table.setParent(None)
        self.advanced_table.deleteLater()
        self.advanced_table = QFrame(self.advanced_hidden_frame)
        self.advanced_table.setLayout(QGridLayout())
        self.advanced_hidden_frame.layout().addWidget(self.advanced_table, 0, 0)
        self.advanced_table.layout().addWidget(QLabel('Intention'), 0, 0)
        self.advanced_table.layout().addWidget(QLabel('|'), 0, 1)
        self.advanced_table.layout().addWidget(QLabel('Contexts'), 0, 2)
        self.advanced_table.layout().addWidget(QLabel('|'), 0, 3)
        self.advanced_table.layout().addWidget(QLabel('Influence Value'), 0, 4)
        self.advanced_table.setFont(font)
        row = 1
        for intention, context_influence in self.bayesNet.config['intentions'].items():
            for context in context_influence:
                if isinstance(context, tuple):
                    for j in range(len(list(context_influence[context]))):
                        key = list(context_influence[context])[j]
                        # For every combined case make a label and a button
                        self.advanced_table.layout().addWidget(
                            QLabel(f'{intention}'), row, 0)
                        self.advanced_table.layout().addWidget(QLabel('|'), row, 1)
                        # build context String
                        context_string = ""
                        for i, _context in enumerate(context):
                            context_string += f'{_context}={str(key[i])}, '
                        context_string = context_string[:-2]
                        self.advanced_table.layout().addWidget(QLabel(context_string), row, 2)
                        self.advanced_table.layout().addWidget(QLabel('|'), row, 3)
                        self.advanced_table.layout().addWidget(
                            QLabel(f'{list(context_influence[context].values())[0]}'), row, 4)
                        remove_button = QPushButton('remove')
                        instantiations = list(
                            context_influence[context].keys())[0]
                        remove_button.clicked.connect(
                            lambda _, intention=intention, contexts=context, instantiations=instantiations:
                            self.remove_combined_influence(intention, contexts, instantiations))
                        self.advanced_table.layout().addWidget(remove_button, row, 5)
                        row += 1

    def remove_combined_influence(self, intention: str, contexts: tuple, instantiations: tuple):
        """
        Remove a combined influence from the BayesNet and update the advanced table.
        """
        self.bayesNet.del_combined_influence(
            intention, contexts, instantiations)
        self.fill_advanced_table()

    def setup_layout(self):
        """
        Setting up the layout of the GUI.
        """

        uic.loadUi(Path(Path(__file__).parent, 'configurator.ui'), self)
        self.grid_layout.setVerticalSpacing(5)

        self.load_button.clicked.connect(self.load)
        self.save_button.clicked.connect(self.save)
        self.decision_threshold_entry.textChanged.connect(
            self.decision_threshold_changed)

        self.error_label.setText("")

        self.context_instantiations = defaultdict(dict)
        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))

        self.new_context_button.clicked.connect(self.new_context)
        self.edit_context_button.clicked.connect(self.edit_context)
        self.delete_context_button.clicked.connect(self.delete_context)

        self.new_intention_button.clicked.connect(self.new_intention)
        self.edit_intention_button.clicked.connect(self.edit_intention)
        self.delete_intention_button.clicked.connect(self.delete_intention)

        self.new_combined_influence_button.clicked.connect(
            self.new_combined_influence)

        self.advanced_label.setText("advanced \u25BC")
        self.advanced_label.setParent(self.advanced_hidden_frame)
        self.advanced_folded = False
        self.advanced_label.clicked.connect(self.on_clicked_advanced)
        
        self.COLORS = {0: 'White', 1: 'Red', 2: 'Orange',
                       3: 'Yellow', 4: 'darkCyan', 5: 'Green'}
        # Adding the canvas
        layout = QGridLayout()
        self.canvas_frame.setLayout(layout)
        self.canvas_frame.layout().addWidget(self.win, 0, 0)
        self.actionOpen.triggered.connect(self.load)
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionAbout.triggered.connect(self.open_link)
        self.actionAbout.setShortcut("F1")
        self.actionNew.triggered.connect(self.reset)
        self.actionNew.setShortcut("Ctrl+N")
        self.actionSave.triggered.connect(self.save)
        self.actionSave.setShortcut("Ctrl+S")
        self.actionSave_as.triggered.connect(self.save_as)
        self.actionSave_as.setShortcut("Ctrl+Shift+S")
        
    def reset(self):
        """
        Resets the state of the Configurator to its initial state.
        """
        self.bayesNet = BayesNet(None)
        self.create_fields()
        self.view.clear()

    def open_link(self):
        url = "https://dfki-ric.github.io/CoBaIR/"
        webbrowser.open_new_tab(url)

    def decision_threshold_changed(self, value):
        """
        Callback for change of the decision threshold.
        """
        self.error_label.setText("")
        try:
            self.bayesNet.change_decision_threshold(
                float(value))
        except AssertionError as error_message:
            self.error_label.setText(f"{error_message}")
        except ValueError:
            self.error_label.setText('Decision Threshold must be a number')

    def set_context_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for a context optionMenu with the options and corresponding command.

        Args:
            options: A list containing the options in the context dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.context_selected
        self.context_selection.clear()

        if options:
            self.context_selection.addItems(list(options))
            max_width = max(QFontMetrics(self.context_selection.font()).boundingRect(option).width() 
                            for option in options)
            self.context_selection.setMinimumWidth(
                max_width + 25)
            self.context_selection.setCurrentIndex(0)
            self.context_selection.currentTextChanged.connect(command)
        else:
            self.context_selection.addItem('Context')
            self.context_selection.currentTextChanged.connect(command)
        command(self.context_selection.currentText())

    def draw_graph(self):
        '''
        This draws the graph from the current config.
        '''
        # only if config is valid
        if self.bayesNet.valid:
            self.graph_item.set_config(self.bayesNet.config)

    def set_influencing_context_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for the influencing context optionMenu 
            with the options and the corresponding command.

        Args:
            options: A list containing the options in the influencing context dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.influencing_context_selected
        self.influencing_context_selection.clear()
        if options:
            self.influencing_context_selection.addItems(list(options))
            max_width = max(QFontMetrics(self.influencing_context_selection.font()).boundingRect(option).width() 
                            for option in options)
            self.influencing_context_selection.setMinimumWidth(
                max_width + 25)  # add some padding
            self.influencing_context_selection.setCurrentIndex(0)
            self.influencing_context_selection.currentTextChanged.connect(
                command)
        else:
            self.influencing_context_selection.addItem('Context')
            self.influencing_context_selection.currentIndexChanged.connect(
                command)
        command(self.influencing_context_selection.currentText())

    def set_intention_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for a intention optionMenu 
            with the options and the corresponding command

        Args:
            options: A list containing the options in the intention dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.influencing_context_selected
        self.intention_dropdown.clear()

        if options:
            self.intention_dropdown.addItems(list(options))
            max_width = max(QFontMetrics(self.influencing_context_selection.font()).boundingRect(option).width() 
                            for option in options)
            self.intention_dropdown.setMinimumWidth(
                max_width + 25)  # add some padding
            self.intention_dropdown.setCurrentIndex(0)
            self.intention_dropdown.currentTextChanged.connect(command)
        else:
            self.intention_dropdown.addItem('Intention')
            self.intention_dropdown.currentIndexChanged.connect(command)

        command(self.intention_dropdown.currentText())

    def context_selected(self, context: str):
        """
        Callback for click on context in context dropdown.

        Args:
            context: name of the clicked context
        """
        logger = logging.getLogger(__name__)
        for _, instantiations in self.context_instantiations.items():
            for instantiation, widgets in instantiations.items():
                for widget in widgets:
                    try:
                        widget.deleteLater()
                    except RuntimeError as e:
                        logger.error(f"Failed to destroy widget {widget}: {type(e).__name__}: {str(e)}")
                    except AttributeError:
                        pass  # can not destroy StringVars
                    except TypeError as e:
                        logger.error(f"Failed to destroy widget {widget}: {type(e).__name__}: {str(e)}")

        self.context_instantiations = defaultdict(dict)

        if context not in self.bayesNet.config['contexts']:
            return
        config = self.bayesNet.config

        layout = QGridLayout()
        self.context_selected_frame.setLayout(layout)
        layout = self.context_selected_frame.layout()

        layout.setVerticalSpacing(10)
        row_count = layout.rowCount()

        for instantiation, value in config['contexts'][context].items():
            instantiation_str = str(instantiation) if isinstance(
                instantiation, bool) else instantiation
            label = QLabel(instantiation_str, self.context_selected_frame)
            label.setFont(QFont('Times New Roman', 13))
            line_edit = QLineEdit(str(value), self.context_selected_frame)
            line_edit.setFont(QFont('Times New Roman', 13))
            line_edit.textChanged.connect(lambda text, context=context, instantiation=instantiation:
                                          self.apriori_values_changed(
                                              text, context=context, instantiation=instantiation)
                                          )

            layout.addWidget(label, row_count, 0)
            layout.addWidget(line_edit, row_count, 1)

            self.context_instantiations[context][instantiation] = (
                label,
                line_edit,
            )
            row_count += 1

    def influencing_context_selected(self, context_or_intention: str):
        """
        Callback for click on context in influencing context dropdown.

        Args:
            context_or_intention: name of the clicked context
        """
        for active_intention, active_context in self.intention_instantiations.items():
            for active_context, instantiations in active_context.items():
                for instantiation, widgets in instantiations.items():
                    for widget in widgets:
                        try:
                            widget.deleteLater()
                        except AttributeError:
                            pass  # can not destroy StringVars
                        except Exception as e:
                            # TODO: better logging
                            print(f"couldn't destroy: {e}")
        intention = self.intention_dropdown.currentText()
        context = self.influencing_context_selection.currentText()
        if context not in self.bayesNet.config['contexts'] or \
                intention not in self.bayesNet.config['intentions']:
            return

        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))

        layout = QGridLayout()
        self.influencing_context_frame.setLayout(layout)
        layout = self.influencing_context_frame.layout()

        layout.setVerticalSpacing(10)
        row_count = layout.rowCount()

        for instantiation, value in self.bayesNet.config['intentions'][intention][context].items():
            influence_text = f'Influence of {context}:{instantiation} on {intention}: LOW'
            instantiation_label = QLabel(
                influence_text, self.influencing_context_frame)

            instantiation_label.setFont(QFont('Times New Roman', 13))
            slider = QSlider(Qt.Horizontal, self.influencing_context_frame)
            slider.setFixedSize(100, 20)

            high_label = QLabel('HIGH', self.influencing_context_frame)
            high_label.setFont(QFont('Times New Roman', 13))

            layout.addWidget(instantiation_label, row_count, 0)
            layout.addWidget(slider, row_count, 1)
            layout.addWidget(high_label, row_count, 2)

            slider.setMinimum(0)
            slider.setMaximum(5)
            slider.setTickInterval(1)
            slider.setStyleSheet(
                f"QSlider::handle:horizontal {{background-color: {self.COLORS[value]}}}")
            slider.setValue(value)

            slider.valueChanged.connect(lambda value, context=context, intention=intention,
                                        instantiation=instantiation, slider=slider:
                                        self.influence_values_changed(value, context, intention, instantiation, slider))

            self.intention_instantiations[intention][context][instantiation] = (
                instantiation_label,
                slider,
                high_label,
            )

            row_count += 1

    def load(self):
        """
        opens a askopenfilename dialog to load a config
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(
            None, "Choose Config", "", "Yaml files (*.yml);;All Files (*)", options=options)
        if fileName:
            try:
                self.error_label.setText("loading BayesNet...")
                self.bayesNet.load(fileName)
                self.error_label.setText("")
            except AssertionError as error_message:
                self.error_label.setText(str(error_message))
            except Exception as error_message:
                self.error_label.setText(str(error_message))
        self.create_fields()


    def get_save_file_path(self, title, default_name, file_filter):
        """
        Opens a save file dialog and returns the selected file path.
        """
        parser = argparse.ArgumentParser(description='Process YAML file path.')
        parser.add_argument('--file', type=str, help='path of YAML file')
        args = parser.parse_args()
        yaml_file_path = args.file
        options = QFileDialog.Options()
        current_file_name = getattr(self.bayesNet, 'file_name', None)
        if current_file_name is None:
            current_file_name = os.path.basename(yaml_file_path) if yaml_file_path else default_name
        file_path, _ = QFileDialog.getSaveFileName(
            None, title, current_file_name, file_filter, options=options)
        return file_path, yaml_file_path

    def save(self):
        """
        Saves the current configuration to a file without asking for confirmation if it exists,
        or asks for a filename if it's a new configuration.
        """
        filetypes = "Yaml files (*.yml);;All Files (*)"
        current_file_name = getattr(self.bayesNet, 'file_name', None)
        if current_file_name:
            save_filepath = current_file_name
        else:
            save_filepath, _ = self.get_save_file_path("Save Config", ".yml", filetypes)

        if save_filepath:
            self.bayesNet.save(save_filepath)
            self.original_config = self.bayesNet.config
            
    def save_as(self):
        """
        Opens a save file dialog to save a configuration with a new name or at a new location.
        If a filename has been previously loaded or saved, that filename will be used as the default.
        """
        filetypes = "Yaml files (*.yml);;All Files (*)"
        save_filepath, _ = self.get_save_file_path("Save As", "default_name.yml", filetypes)


    def closeEvent(self, event):
        """
        Override the closeEvent method to prompt the user to save changes made to the configuration
        before closing the application.

        :param event: The close event.
        :type event: QtGui.QCloseEvent

        :return: None
        """
        if self.bayesNet.config != self.original_config:
            reply = QMessageBox.question(self, 'Save Changes', 'Do you want to save the changes made to the configuration?',
                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                self.save_as()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def apriori_values_changed(self, *args, context, instantiation):
        """
        Callback for change of the apriori values.

        Args:
            context: name of the context
            instantiation: name of the corresponding instantiation
        """
        # update config
        self.error_label.setText("")
        try:
            self.bayesNet.change_context_apriori_value(context=context, instantiation=instantiation, value=float(
                self.context_instantiations[context][instantiation][1].text()))
        except AssertionError as error_message:
            self.error_label.setText(str(error_message))
        except ValueError:
            self.error_label.setText(
                f'Apriori probability of context "{context}.{instantiation}" is not a number')

    def influence_values_changed(self, value, context, intention, instantiation, slider):
        """
        Callback for change of the influence values.

        Args:
            value: new influence value
            context: name of the context
            intention: name of the intention
            instantiation: name of the corresponding instantiation
            slider: handle to the slider which should change its color
        """
        self.error_label.setText("")
        try:
            self.bayesNet.change_influence_value(
                intention=intention, context=context, instantiation=instantiation, value=int(value))
            slider.setStyleSheet(
                f"QSlider::handle:horizontal {{background-color: {self.COLORS[value]}}}")
        except AssertionError as e:
            self.error_label.setText(str(e))
        return value

class TwoLayerGraph(pg.GraphItem):
    """
    Graph Visualization for the two layer bayesian network
    """

    def __init__(self, dist=10, size=3, line_width=[0, 25], pxMode=False, **kwds):
        super().__init__(**kwds)
        self.dist = dist
        self.size = size
        self.line_width = line_width
        self.pxMode = pxMode
        self.unfolded_context = set()
        self.textItems = []

    def _set_pos(self):
        """
        Add all the data points in the pos array
        """
        i = 0
        added_context = set()
        for intention, context_dict in self.config['intentions'].items():
            position = (self.dist, self.dist/2 + i*self.dist)
            self.data["pos"].append(position)
            self.data["names"].append(intention)
            self.data["intention_indices"].append(i)
            # self.data["mapping"][position] = intention
            i += 1
            for context, instantiation_dict in context_dict.items():
                if context not in added_context and isinstance(context, str):
                    if context in self.unfolded_context:
                        for instatiation in instantiation_dict:
                            if f"{context}:{instatiation}" not in added_context and isinstance(context, str):
                                position = (0, i*self.dist)
                                self.data["pos"].append(position)
                                self.data["names"].append(
                                    (context, instatiation))
                                # f"{context}:{instatiation}")
                                # TODO: use tuple here and check for type on usage
                                # TODO: this may be 'instantiation_indices'
                                self.data["instantiation_indices"].append(i)
                                # self.data["context_indices"].append(i)
                                # self.data["mapping"][position] = f"{context}:{instatiation}"
                                added_context.add(f"{context}:{instatiation}")
                                i += 1
                    else:
                        position = (0, i*self.dist)
                        self.data["pos"].append(position)
                        self.data["names"].append(context)
                        self.data["context_indices"].append(i)
                        # self.data["mapping"][position] = context
                        added_context.add(context)
                        i += 1

    def _set_adj(self):
        """
        Add all the connections in the adj array
        """
        # TODO: merge context and instantiations indices
        left_side = self.data["context_indices"] + \
            self.data["instantiation_indices"]
        self.data["adj"] = list(itertools.product(
            left_side, self.data["intention_indices"]))

    def _set_pen(self):
        """
        Add all the pens for the connections in the pen array 
        """
        for start, end in self.data["adj"]:
            if start in self.data["context_indices"] or start in self.data["instantiation_indices"]:
                context = self.data["names"][start]
                intention = self.data["names"][end]
            else:
                context = self.data["names"][end]
                intention = self.data["names"][start]
            color = pg.mkPen().color()
            normalized_mean = np.mean(
                list(self.config["intentions"][intention][context].values()))/5.0

            if start in self.data["instantiation_indices"]:
                # HAck: TODO: this is problematic if the context has a colon in name
                context, instantiation = self.data["names"][start]
                # TODO. problem with default dict or problem with type - for "human holding object" bool is used and it does not work...
                normalized_mean = self.config["intentions"][intention][context][instantiation] / 5.0
            alpha = color.alpha()
            # TODO: Maybe color can even be scaled with the normalized mean
            red = color.red() if normalized_mean else 255
            green = color.green() if normalized_mean else 0
            blue = color.blue() if normalized_mean else 0
            width = self.line_width[0] + \
                (self.line_width[1] - self.line_width[0]) * normalized_mean

            self.data["pen"].append(np.array([(red, green, blue, alpha, width)], dtype=[
                ('red', np.uint8), ('green', np.uint8), ('blue', np.uint8), ('alpha', np.uint8), ('width', np.uint8)]))

    def _set_text(self):
        """
        Place all the texts for Context and Intention Names
        """
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        # self.data["mapping"].items():
        for position, label in zip(self.data["pos"], self.data["names"]):
            # TODO: change color
            if isinstance(label, tuple):
                label = f"{label[0]}:{label[1]}"
            text_item = pg.TextItem(label, anchor=(0.5, 0.5))
            text_item.setParentItem(self)
            text_item.setPos(*position)
            text_item.setPlainText(label)
            self.textItems.append(text_item)

    def set_config(self, config):
        """
        Uses the config to set the data
        """
        # extract every needed field for setData from config

        self.config = config
        self.data = {"mapping": {}, "pos": [],
                     "adj": [], "pen": [], "names": [], "context_indices": [], "intention_indices": [], "instantiation_indices": []}
        self._set_pos()
        self._set_adj()
        self._set_pen()
        self._set_text()

        self.setData(pos=np.array(self.data["pos"]), adj=np.array(
            self.data["adj"]), pen=np.array(self.data["pen"]), size=self.size, pxMode=self.pxMode)

    def mousePressEvent(self, event):
        """
        Handler for the mouse click event
        """
        click_pos = event.pos()
        # Context
        if click_pos.x() > 0 - (self.size/2.0) and click_pos.x() < 0 + (self.size/2.0):
            # self.data["mapping"].items():
            i = 0
            for position, name in zip(self.data["pos"], self.data["names"]):
                if click_pos.y() > position[1] - (self.size/2.0) and click_pos.y() < position[1] + (self.size/2.0) and position[0] == 0:
                    # click on folded context
                    if i in self.data["context_indices"]:
                        self.unfolded_context.add(name)
                    # click on one of the instantiations of an unfolded context
                    if i in self.data["instantiation_indices"]:
                        # HAck: TODO: this is problematic if the context has a colon in name
                        context, instantiation = self.data["names"][i]
                        self.unfolded_context.remove(context)
                i += 1
        # Intention
        if click_pos.x() > self.dist - (self.size/2.0) and click_pos.x() < self.dist + (self.size/2.0):
            pass
            # TODO: maybe set the focus to the corresponding field

        self.set_config(self.config)
