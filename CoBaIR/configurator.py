'''
This module is a GUI configurator to create configurations for context based intention recognition - it can as well be used in a live mode to test the configuration
'''

# System imports
import sys
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.simpledialog import Dialog
from tkinter import ttk
from copy import deepcopy
from types import FunctionType as function
from pathlib import Path

import yaml
# 3rd party imports

# local imports
from .bayes_net import BayesNet, load_config
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics


# end file header
__author__ = 'Adrian Lubitz'


class NewIntentionDialog(Dialog):
    """Dialog Window for new Intention"""

    def __init__(self, parent, title: str = ..., intention: str = None) -> None:
        """
        Extends the Constructor of Dialog to use an already existing intention.

        If an intention is given it will be filled in the corresponding text field.

        Args:
            intention: An intention that will be filled in the dialog
        """
        self.intention = intention
        super().__init__(parent, title)

    def body(self, master):
        """
        Sets the Layout.

        Args:
            master: the master window this dialog belongs to
        Returns:
            tk.Entry:
                the initial focus
        """

        tk.Label(master, text="New Intention:").grid(row=0)
        self.intention_entry = tk.Entry(master)
        if self.intention:
            self.intention_entry.insert(0, self.intention)
        self.intention_entry.grid(row=1)
        return self.intention_entry  # initial focus

    def validate(self):
        """
        highlights empty fields

        Returns:
            bool:
                True if the entry is not empty
        """
        if not self.intention_entry.get():
            # mark red
            self.intention_entry.configure(highlightbackground='red',
                                           selectbackground='red', highlightcolor='red')
            return False
        else:
            return True

    def apply(self):
        """
        Applies the result to hand it over to the master
        """
        self.result = self.intention_entry.get()


class NewCombinedContextDialog(Dialog):
    """Dialog Window for new combined Context influence"""

    def __init__(self, parent, title: str = ..., intentions: dict = None) -> None:
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
        super().__init__(parent, title)

    def body(self, master):
        """
        Sets the Layout.

        Args:
            master: the master window this dialog belongs to
        """
        # intention
        intention_frame = tk.Frame(master)
        intention_frame.grid(row=0)
        tk.Label(intention_frame, text='Intention:').grid(row=0, column=0)
        values = list(self.intentions.keys())
        self.intention_selection = tk.StringVar(
            intention_frame, values[0])
        tk.OptionMenu(
            intention_frame, self.intention_selection, *values).grid(row=0, column=1)

        # Value:
        value_frame = tk.Frame(master)
        value_frame.grid(row=2)
        tk.Label(value_frame, text='Influence value:').grid(row=0, column=0)
        self.value_selection = tk.StringVar(value_frame, 0)
        tk.OptionMenu(
            value_frame, self.value_selection, *[0, 1, 2, 3, 4, 5]).grid(row=0, column=1)

        # Button
        button_frame = tk.Frame(master)
        button_frame.grid(row=3)
        tk.Button(button_frame, command=self.new_instantiation,
                  text='additional context').grid()
        self.error_label = tk.Label(button_frame, fg='#f00')
        self.error_label.grid(row=1)

        # contexts
        self.contexts = {}
        for context, instantiations in list(self.intentions.values())[0].items():
            if not isinstance(context, tuple):
                self.contexts[context] = instantiations
        self.context_frame = tk.Frame(master)
        self.context_frame.grid(row=1)
        tk.Label(self.context_frame, text='Context').grid(row=0, column=0)
        tk.Label(self.context_frame, text='Instantiation').grid(
            row=0, column=1)
        self.context_selections = []
        self.context_menus = []
        self.instantiation_selections = []
        self.instantiation_menus = []
        for i in range(2):
            self.new_instantiation()

    def context_selected(self, context: str, i: int):
        """
        Callback for context selection in dropdown

        Args:
            context: A context name
            i: the position of the dropdown menu
        """
        self.instantiation_menus[i].grid_remove()
        self.instantiation_menus[i].destroy()
        for inst in self.contexts[context]:
            self.original_instantiations[context][str(inst)] = inst
        instantiations = list(self.original_instantiations[context].keys())
        self.instantiation_menus[i] = tk.OptionMenu(
            self.context_frame, self.instantiation_selections[i], *instantiations)
        self.instantiation_menus[i].grid(row=i+1, column=1)
        self.instantiation_selections[i].set(
            str(list(self.contexts[context].keys())[0]))
        # available context -> every dropdown should only have available + selected
        available_context = self._eval_available_context()
        for i_m, menu in enumerate(self.context_menus):
            menu.grid_remove()
            menu.destroy()
            contexts = [self.context_selections[i_m].get()] + available_context
            self.context_menus[i_m] = tk.OptionMenu(
                self.context_frame, self.context_selections[i_m], *contexts, command=lambda x, i=i_m: self.context_selected(x, i))
            self.context_menus[i_m].grid(row=i_m+1, column=0)

    def _eval_available_context(self):
        """
        evaluate which contexts are available for the dropdown

        Returns:
            list:
                A list of available contexts
        """
        available_context = list(self.contexts.keys())
        for selection in self.context_selections:
            available_context.remove(selection.get())
        return available_context

    def new_instantiation(self):
        """
        Creates new Entries to input more context instantiations
        """
        available_context = self._eval_available_context()
        i = len(self.context_selections)
        if not available_context:
            self.error_label['text'] = 'No more context available'
            return
        self.context_selections.append(tk.StringVar(
            self.context_frame, available_context[0]))
        self.instantiation_selections.append(
            tk.StringVar(self.context_frame, list(self.contexts[available_context[0]].keys())[0]))
        self.context_menus.append(tk.OptionMenu(
            self.context_frame, self.context_selections[-1], *available_context, command=lambda x, i=i: self.context_selected(x, i)))
        self.context_menus[-1].grid(row=i+1, column=0)
        instantiations = list(self.contexts[available_context[0]].keys())
        self.instantiation_menus.append(tk.OptionMenu(
            self.context_frame, self.instantiation_selections[-1], *instantiations))
        self.instantiation_menus[-1].grid(row=i+1, column=1)
        self.context_selected(self.context_selections[-1].get(), i)

    def apply(self):
        """
        Applies the result to hand it over to the master
        """
        intention = self.intention_selection.get()
        value = self.value_selection.get()
        contexts = []
        instantiations = []
        for i, context_selection in enumerate(self.context_selections):
            contexts.append(context_selection.get())
            instantiations.append(
                self.original_instantiations[context_selection.get()][self.instantiation_selections[i].get()])
        # intention: str, contexts: tuple, instantiations: tuple, value: int
        self.result = {'intention': intention, 'value': int(value), 'contexts': tuple(
            contexts), 'instantiations': tuple(instantiations)}


class NewContextDialog(QDialog):
    """Dialog Window for new Context"""

    def __init__(self, parent = None, predefined_context: dict = None) -> None:
        """
        Extends the Constructor of Dialog to use already existing context and the corresponding instantiations and values.

        If context and their corresponding instantiations and values are given it will be filled in the corresponding text fields.

        Args:
            predefined_context:
                Context with the corresponding instantiations.
                Example: {'speech commands': {
                    'pickup': 0.2, 'handover': 0.2, 'other': 0.6}}
        """
        dialog = QDialog()
        # Do something with the dialog
        dialog.deleteLater()
        self.predefined_context = deepcopy(predefined_context)
        super().__init__(parent)  
        self.result = None          
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
        self.grid_layout_2 = self.findChild(QGridLayout, 'gridLayout_2')
        self.context_entry = self.findChild(QLineEdit, 'context_entry')
        self.instantiations_frame = self.findChild(QFrame, 'instantiations_frame')
        self.instantiations = []
        self.shown_instantiations = 0 
        self.grid_layout = QGridLayout()
        self.instantiations_frame.setLayout(self.grid_layout)
        self.instantiations_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)   
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
            if instantiations:
                # get name
                name = list(instantiations.keys())[0]
                # get value
                value = instantiations[name]
                # set entries
                name_entry.setText(name)
                probability_entry.setText(str(value))
                # del entry
                del(instantiations[name])
            self.grid_layout.addWidget(name_entry, self.shown_instantiations+1, 0)
            self.grid_layout.addWidget(probability_entry, self.shown_instantiations+1, 1)
            self.instantiations.append((name_entry, probability_entry))
            self.shown_instantiations += 1
        self.more = self.findChild(QPushButton, 'pushButton')
        self.more.clicked.connect(self.new_instantiation)
        return self.context_entry

    def remove_instantiation(self, index):
        """
        Callback for the remove_button
        Args:
            index: the index in self.instantiations
        """
        for element in self.instantiations[index]:
            element.hide()
            element.deleteLater()
        self.shown_instantiations -= 1
        # TODO: that is problematic because it shifts indexes!!!
        # Or I need to redraw the whole thing like I always do...
        self.instantiations.itemAt(index).widget().deleteLater()
        for index, instantiation in enumerate(self.instantiations):
            # or I just need to rebind callback with correct index works with configure(command=...)
            instantiation[2].clicked.connect(lambda x=index: self.remove_instantiation(x))

    def new_instantiation(self):
        """
        Creates two new Entries to input more instantiations
        """
        name_entry = QLineEdit(self.instantiations_frame)
        probability_entry = QLineEdit(self.instantiations_frame)
        self.grid_layout.addWidget(name_entry, self.shown_instantiations+1, 0)
        self.grid_layout.addWidget(probability_entry, self.shown_instantiations+1, 1)
        remove_button = QPushButton('-', self.instantiations_frame)
        remove_button.clicked.connect(lambda x=self.shown_instantiations: self.remove_instantiation(x))
        self.grid_layout.addWidget(remove_button, self.shown_instantiations + 1, 2)
        self.instantiations.append(
            (name_entry, probability_entry, remove_button ))
        self.shown_instantiations += 1

    def validate(self):
        """
        highlights empty fields

        Returns:
            bool:
                True if the entries are not empty
        """

        # TODO: entries cannot be the same (len(entries) must be the same as len(set(entries.get())))

        valid = True
        instantiation_names = []
        # more than 1 entry is needed!!!
        if len(self.instantiations) < 2:
            valid = False
            # TODO: point out why not valid
        empty_entries = []
        self.context_entry.setStyleSheet("QLineEdit { background-color: black; color: black; selection-background-color: black; }")  # TODO: Too much I only want the text to be black/normal...
        if not self.context_entry.text():
            empty_entries.append(self.context_entry)
        for i, instantiation in enumerate(self.instantiations):
            # Only setting colors for the entry fields
            for entry in instantiation[0:2]:
                entry.setStyleSheet("QLineEdit { background-color: black; color: black; selection-background-color: black; }")
                if not entry.text():
                    empty_entries.append(entry)
            name = instantiation[0].text()
            if name in instantiation_names:
                # mark red
                print('mark red')
                instantiation[0].setStyleSheet("QLineEdit { background-color: red; color: red; selection-background-color: red; }")
                valid = False
            instantiation_names.append(name)
        if empty_entries:
            # mark red
            for entry in empty_entries:
                entry.setStyleSheet("QLineEdit { background-color: red; color: red; selection-background-color: red; }")
            valid = False
        return valid

    def get_result(self):
        result = defaultdict(lambda: defaultdict(dict))
        for instantiation in self.instantiations:
            key = instantiation[0].text()
            value = float(instantiation[1].text())
            result[self.context_entry.text()][key] = value
        self.accept()
        return result

class Configurator(QtWidgets.QMainWindow):
    '''
    GUI configurator to create configurations for context based intention recognition.
    It can as well be used in a live mode to test the configuration
    '''

    def __init__(self, config: dict = None, *args, **kwargs):
        '''
        Setting up the GUI

        Args:
            config: A dict with a config following the config format.
        '''
        self.app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setup_layout()
        self.bayesNet = BayesNet(config)
        self.create_fields()
        self.show()  # Show the GUI

    def set_error_label_red(self):
        """
        setting the alignment and color of the error label
        """
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red")

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

    def set_decision_threshold(self):
        """
        This sets value in the decision threshold entry from the config
        """
        self.decision_threshold_entry.setText(
            str(self.bayesNet.config['decision_threshold']))

    def adjust_button_visibility(self):
        """
        Adjusts if buttons are visible or not.

        Buttons for edit and delete will only be visible if there is a corresponding intention or context already created.
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
        # remove errorText
        self.error_label.setText("")
        # open small dialog to create context
        dialog = NewContextDialog(self)
        
        def update_and_close():
            result = dialog.get_result()
            # check if context already exists!
            # it's always only one new context
            new_context = list(result.keys())[0]
            try:
                self.bayesNet.add_context(new_context, result[new_context])
            except AssertionError as e:
                self.error_label.setText(str(e))
            # update view!
            self.create_fields()
            self.context_selection.setCurrentText(new_context)
            # Explicit call is necessary because setCurrentText seems not to trigger the callback
            self.context_selected(new_context)
            dialog.accept()

        ok_button = dialog.findChild(QPushButton, "pushButton_2")
        ok_button.clicked.connect(update_and_close)
        cancel_button = dialog.findChild(QPushButton, "pushButton_3")
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()

    def edit_context(self):
            """
            Edit the currently selected context.

            !!! note
            Changing the name of an instantiation will always set the influence value of this instantiation to zero for all intentions!

            !!! note
            The GUI can only handle strings for now. This means every instantiation name will be casted to a string upon editing.
            """
            # TODO: renaming instantiations should not neccesarily put influence values to zero - check cases
            # TODO: this will always set the instantiations as Strings
            # Open the new Context dialog with prefilled values
            # remove errorText
            self.error_label.setText("")
            # open small dialog to create context
            context = self.context_selection.currentText()
            instantiations = self.bayesNet.config['contexts'][context]
            dialog = NewContextDialog(self, predefined_context={
                                    context: instantiations})
            
            def update_and_close():
                result = dialog.get_result()
                try:
                    # it's always only one new context
                    new_context_name = list(result.keys())[0]
                    new_instantiations = result[new_context_name]
                    self.bayesNet.edit_context(
                        context, new_instantiations, new_context_name)
                except AssertionError as e:
                    self.error_label.setText(str(e))
                self.create_fields()
                self.context_selection.setCurrentText(new_context_name)
                # Explicit call is neccessary because set seems not to trigger the callback
                self.context_selected(new_context_name)
                dialog.accept()

            ok_button = dialog.findChild(QPushButton, "pushButton_2")
            ok_button.clicked.connect(update_and_close)
            cancel_button = dialog.findChild(QPushButton, "pushButton_3")
            cancel_button.clicked.connect(dialog.reject)
            dialog.exec_()

    def delete_context(self):
        """"
        Deletes the currently selected context.
        """
        self.error_label['text'] = f""
        context = self.context_selection.get()
        try:
            self.bayesNet.del_context(context)
        except AssertionError as e:
            self.error_label['text'] = f"{e}"
        self.create_fields()

    def new_intention(self):
        """
        Open a new Dialog to create new intentions.
        """
        # remove errorText
        self.error_label['text'] = f""
        dialog = NewIntentionDialog(self, title="New Intention")
        if dialog.result:
            try:
                self.bayesNet.add_intention(dialog.result)
            except AssertionError as e:
                self.error_label['text'] = f"{e}"
            # update view!
            self.create_fields()
            self.intention_selection.set(dialog.result)
            # Explicit call is neccessary because set seems not to trigger the callback
            self.influencing_context_selected(dialog.result)

    def edit_intention(self):
        """
        Edit the name of the currently selected intention
        """

        self.error_label['text'] = f""
        # open small dialog to create context
        intention = self.intention_selection.get()
        dialog = NewIntentionDialog(self,
                                    title="Edit Intention", intention=intention)
        if dialog.result:
            try:
                self.bayesNet.edit_intention(intention, dialog.result)
            except AssertionError as e:
                self.error_label['text'] = f"{e}"
            self.create_fields()
            self.intention_selection.set(dialog.result)
            # Explicit call is neccessary because set seems not to trigger the callback
            self.influencing_context_selected(dialog.result)

    def delete_intention(self):
        """
        Delete the currently selected intention
        """
        self.error_label['text'] = f""
        intention = self.intention_selection.get()
        try:
            self.bayesNet.del_intention(intention)
        except AssertionError as e:
            self.error_label['text'] = f"{e}"
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
        else:
            # Change text back to down arrow
            self.advanced_label.setText("advanced \u25BC")
            self.advanced_folded = True
            self.advanced_hidden_frame.hide()

    def new_combined_influence(self):
        """
        Callback for the button
        """
        self.error_label['text'] = f""
        dialog = NewCombinedContextDialog(
            self, title="New combined Context influence", intentions=self.bayesNet.config['intentions'])
        if dialog.result:
            try:
                self.bayesNet.add_combined_influence(
                    intention=dialog.result['intention'], contexts=dialog.result['contexts'], instantiations=dialog.result['instantiations'], value=dialog.result['value'])
            except ValueError as e:
                self.error_label['text'] = f"{e}"
            self.create_fields()

    def fill_advanced_table(self):
        '''
        Fill the content of the table containing combined influence values
        '''

        font = QFont()
        font.setPointSize(13)
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
                        key = (list(context_influence[context])[j])
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
                        remove_button.clicked.connect(lambda _, intention=intention, contexts=context, instantiations=list(
                            context_influence[context].keys())[0]: self.remove_combined_influence(intention, contexts, instantiations))
                        self.advanced_table.layout().addWidget(remove_button, row, 5)
                        row += 1

    def remove_combined_influence(self, intention: str, contexts: tuple, instantiations: tuple):
        self.bayesNet.del_combined_influence(
            intention, contexts, instantiations)
        self.fill_advanced_table()

    def setup_layout(self):
        """
        Setting up the layout of the GUI.
        """

        uic.loadUi(Path(Path(__file__).parent, 'configurator.ui'), self)
        self.grid_layout = self.findChild(QGridLayout, 'gridLayout')
        self.grid_layout.setVerticalSpacing(5)

        self.load_button.clicked.connect(self.load)
        self.save_button.clicked.connect(self.save)
        self.decision_threshold_entry.textChanged.connect(
            self.decision_threshold_changed)

        self.error_label = self.findChild(QLabel, 'error_label')
        self.set_error_label_red()
        self.error_label.setText("")

        self.context_label = self.findChild(QLabel, 'intention_label_frame_2')
        self.intention_label_frame = self.findChild(
            QLabel, 'intention_label_frame')
        self.on_label = self.findChild(QLabel, 'label_3')

        self.context_dropdown = self.findChild(QComboBox, 'context_selection')
        self.context_selection = self.context_dropdown

        self.influencing_context_dropdown = self.findChild(
            QComboBox, 'influencing_context_selection')
        self.influencing_context_selection = self.influencing_context_dropdown

        self.intention_dropdown = self.findChild(
            QComboBox, 'intention_selection')
        self.intention_selection = self.intention_dropdown

        self.context_instantiations = defaultdict(dict)

        self.context_selected_frame = self.findChild(QFrame, 'frame_2')
        self.influencing_context_frame = self.findChild(QFrame, 'frame')

        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))

        self.new_context_button = self.findChild(
            QPushButton, 'new_context_button')
        self.new_context_button.clicked.connect(self.new_context)
        
        self.edit_context_button = self.findChild(
            QPushButton, 'edit_context_button')
        self.edit_context_button.clicked.connect(self.edit_context)
        self.delete_context_button = self.findChild(
            QPushButton, 'delete_context_button')

        self.new_intention_button = self.findChild(
            QPushButton, 'new_intention_button')
        self.edit_intention_button = self.findChild(
            QPushButton, 'edit_intention_button')
        self.delete_intention_button = self.findChild(
            QPushButton, 'delete_intention_button')

        self.advanced_hidden_frame = self.findChild(QFrame, 'frame_3')
        self.advanced_label.setText("advanced \u25BC")
        self.advanced_label.setParent(self.advanced_hidden_frame)
        self.advanced_folded = True
        self.advanced_label.clicked.connect(self.on_clicked_advanced)

        self.advanced_table = QFrame(self.advanced_hidden_frame)
        self.advanced_hidden_frame.setLayout(QGridLayout())
        self.advanced_hidden_frame.layout().addWidget(self.advanced_table, 0, 0)
        self.on_clicked_advanced()

        # add widgets to layout
        self.grid_layout.addWidget(self.context_label, 0, 0)
        self.grid_layout.addWidget(self.context_dropdown, 0, 1)
        self.grid_layout.addWidget(self.edit_context_button, 0, 2)
        self.grid_layout.addWidget(self.delete_context_button, 0, 3)

        self.grid_layout.addWidget(self.context_selected_frame, 1, 1)

        self.grid_layout.addWidget(self.intention_label_frame, 2, 0)
        self.grid_layout.addWidget(self.influencing_context_dropdown, 2, 1)
        self.grid_layout.addWidget(self.on_label, 2, 2)
        self.grid_layout.addWidget(self.intention_dropdown, 2, 3)
        self.grid_layout.addWidget(self.edit_intention_button, 2, 4)
        self.grid_layout.addWidget(self.delete_intention_button, 2, 5)

        self.grid_layout.addWidget(self.context_instantiations_3, 4, 1)
        self.grid_layout.addWidget(self.decision_threshold_entry, 4, 2)

        self.grid_layout.addWidget(self.advanced_label, 5, 1)

        self.grid_layout.addWidget(self.advanced_new_button, 7, 1)

        self.grid_layout.addWidget(self.load_button, 8, 1)
        self.grid_layout.addWidget(self.save_button, 8, 2)

    def decision_threshold_changed(self, value):
        """
        Callback for change of the decision threshold.
        """
        self.error_label.setText("")
        try:
            self.bayesNet.change_decision_threshold(
                float(value))
        except AssertionError as e:
            self.error_label.setText(f"{e}")
        except ValueError as e:
            self.error_label.setText(f'Decision Threshold must be a number')

    def set_context_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for a context optionMenu with the options and the corresponding command.

        Args:
            options: A list containing the options in the context dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.context_selected
        # self.context_dropdown.deleteLater()

        if options:
            if options:
                self.context_selection.addItems(list(options))
                max_width = max([QFontMetrics(self.context_dropdown.font()).boundingRect(
                    option).width() for option in options])
                self.context_dropdown.setMinimumWidth(
                    max_width + 25)  # add some padding
                self.context_dropdown.setCurrentIndex(0)
                self.context_dropdown.currentTextChanged.connect(command)
            else:
                self.context_selection.addItem('Context')
            self.context_dropdown.clear()
            self.context_dropdown.addItems(options)
            self.context_dropdown.setCurrentIndex(0)
            self.context_dropdown.currentTextChanged.connect(command)

        else:  # clear
            self.context_selection.addItem("Context")
            values = []
            for value in values:
                self.context_dropdown.addItems(value)
            self.context_dropdown.currentTextChanged.connect(command)
        command(self.context_selection.currentText())

    def set_influencing_context_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for the influencing context optionMenu with the options and the corresponding command.

        Args:
            options: A list containing the options in the influencing context dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.influencing_context_selected
        # self.influencing_context_dropdown.deleteLater()
        if options:
            if options:
                self.influencing_context_selection.addItems(list(options))
                max_width = max([QFontMetrics(self.influencing_context_dropdown.font(
                )).boundingRect(option).width() for option in options])
                self.influencing_context_dropdown.setMinimumWidth(
                    max_width + 25)  # add some padding
                self.influencing_context_dropdown.setCurrentIndex(0)
                self.influencing_context_dropdown.currentTextChanged.connect(
                    command)
            else:
                self.influencing_context_selection.addItem('Context')
            self.influencing_context_dropdown.clear()
            self.influencing_context_dropdown.addItems(options)
            self.influencing_context_dropdown.setCurrentIndex(0)
            self.influencing_context_dropdown.currentIndexChanged.connect(
                command)
        else:  # clear
            self.influencing_context_selection.addItem("Context")
            values = []
            for value in values:
                self.influencing_context_dropdown.addItem(value)
            self.influencing_context_dropdown.currentIndexChanged.connect(
                command)

        command(self.influencing_context_selection.currentText())

    def set_intention_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for a intention optionMenu with the options and the corresponding command

        Args:
            options: A list containing the options in the intention dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.influencing_context_selected
        # self.intention_dropdown.deleteLater()
        if options:
            if options:
                self.intention_selection.addItems(list(options))
                max_width = max([QFontMetrics(self.intention_dropdown.font()).boundingRect(
                    option).width() for option in options])
                self.intention_dropdown.setMinimumWidth(
                    max_width + 25)  # add some padding
                self.intention_dropdown.setCurrentIndex(0)
                self.intention_dropdown.currentTextChanged.connect(command)
            else:
                self.intention_selection.addItem('Intention')
            self.intention_dropdown.clear()
            self.intention_dropdown.addItems(options)
            self.intention_dropdown.setCurrentIndex(0)
            self.intention_dropdown.currentIndexChanged.connect(command)

        else:  # clear
            self.intention_selection.addItem('Intention')
            values = []
            for value in values:
                self.intention_dropdown.addItem(value)
            self.intention_dropdown.currentIndexChanged.connect(command)

        command(self.intention_selection.currentText())

    def context_selected(self, context: str):
        """
        Callback for click on context in context dropdown.

        Args:
            context: name of the clicked context
        """

        for active_context, instantiations in self.context_instantiations.items():
            for instantiation, widgets in instantiations.items():
                for widget in widgets:
                    try:
                        widget.deleteLater()
                    except AttributeError:
                        pass  # can not destroy StringVars
                    except Exception as e:
                        # TODO: better logging
                        print(f"couldn't destroy: {e}")

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
            line_edit.textChanged.connect(lambda text, context=context, instantiation=instantiation: self.apriori_values_changed(text, context=context, instantiation=instantiation)
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
        intention = self.intention_selection.currentText()
        context = self.influencing_context_selection.currentText()
        if context not in self.bayesNet.config['contexts'] or intention not in self.bayesNet.config['intentions']:
            return

        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))

        layout = QGridLayout()
        self.influencing_context_frame.setLayout(layout)
        layout = self.influencing_context_frame.layout()

        layout.setVerticalSpacing(10)
        row_count = layout.rowCount()

        for instantiation, value in self.bayesNet.config['intentions'][intention][context].items():
            instantiation_label = QLabel(
                f'Influence of {context}:{instantiation} on {intention}: LOW', self.influencing_context_frame)
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
            slider.setValue(value)
            slider.valueChanged.connect(lambda value, context=context, intention=intention,
                                        instantiation=instantiation: self.influence_values_changed(value, context, intention, instantiation))

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
            except AssertionError as e:
                self.error_label.setText(str(e))
            except Exception as e:
                self.error_label.setText(str(e))
        self.create_fields()

    def save(self):
        """
        opens a asksaveasfilename dialog to save a config
        """
        filetypes = "Yaml files (*.yml);;All Files (*)"
        save_filepath, _ = QFileDialog.getSaveFileName(
            None, "Save Config", "", filetypes)
        if save_filepath:
            self.bayesNet.save(save_filepath)

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
                self.context_instantiations[context][instantiation][2].get()))
        except AssertionError as e:
            self.error_label.setText(str(e))
        except ValueError as e:
            self.error_label['text'] = f'Apriori probability of context "{context}.{instantiation}" is not a number'

    def influence_values_changed(self, value, context, intention, instantiation):
        """
        Callback for change of the influence values.

        Args:
            value: new influence value
            context: name of the context
            intention: name of the intention
            instantiation: name of the corresponding instantiation
        """
        self.error_label.setText("")
        try:
            self.bayesNet.change_influence_value(
                intention=intention, context=context, instantiation=instantiation, value=int(value))
        except AssertionError as e:
            self.error_label.setText(str(e))

        return value