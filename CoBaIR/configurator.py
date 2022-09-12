'''
This module is a GUI configurator to create configurations for context based intention recognition - it can as well be used in a live mode to test the configuration
'''

# System imports
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.simpledialog import Dialog
from tkinter import ttk
from copy import deepcopy
from types import FunctionType as function

import yaml
# 3rd party imports

# local imports
from .bayes_net import BayesNet

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


class NewContextDialog(Dialog):
    """Dialog Window for new Context"""

    def __init__(self, parent, title: str = ..., predefined_context: dict = None) -> None:
        """
        Extends the Constructor of Dialog to use already existing context and the corresponding instantiations and values.

        If context and their corresponding instantiations and values are given it will be filled in the corresponding text fields.

        Args:
            predefined_context:
                Context with the corresponding instantiations.
                Example: {'speech commands': {
                    'pickup': 0.2, 'handover': 0.2, 'other': 0.6}}
        """
        self.predefined_context = deepcopy(predefined_context)
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
        name_frame = tk.Frame(master)
        name_frame.grid(row=0)
        tk.Label(name_frame, text="Context:").grid(row=0)
        self.context_entry = tk.Entry(name_frame)
        self.context_entry.grid(row=0, column=1)

        # frame for instantiations
        self.instantiations_frame = tk.Frame(master)
        self.instantiations_frame.grid(row=1)
        tk.Label(self.instantiations_frame,
                 text="Instantiation Name").grid(row=0, column=0)
        tk.Label(self.instantiations_frame,
                 text="Apriori Probability").grid(row=0, column=1)
        self.instantiations = []
        self.shown_instantiations = 0
        # TODO: Fill the entries here if predefined_context is given!
        if self.predefined_context:
            # it's always only one new context
            context = list(self.predefined_context.keys())[0]
            instantiations = self.predefined_context[context]
            self.context_entry.insert(0, context)
        else:
            instantiations = {}
        while(self.shown_instantiations < 2 or instantiations):
            # tk.Label(self.instantiations_frame,
            #          text=f"Instantiation {self.shown_instantiations}:").grid(row=self.shown_instantiations)
            name_entry = tk.Entry(self.instantiations_frame)
            probability_entry = tk.Entry(self.instantiations_frame)
            if instantiations:
                # get name
                name = list(instantiations.keys())[0]
                # get value
                value = instantiations[name]
                # set entries
                name_entry.insert(0, name)
                probability_entry.insert(0, value)
                # del entry
                del(instantiations[name])
            name_entry.grid(row=self.shown_instantiations + 1, column=0)
            probability_entry.grid(row=self.shown_instantiations + 1, column=1)
            self.instantiations.append((name_entry, probability_entry))
            self.shown_instantiations += 1

        tk.Button(master, command=self.new_instantiation,
                  text='More').grid(row=2)

        return self.context_entry  # initial focus

    def new_instantiation(self):
        """
        Creates two new Entries to input more instantiations
        """
        name_entry = tk.Entry(self.instantiations_frame)
        probability_entry = tk.Entry(self.instantiations_frame)
        name_entry.grid(row=self.shown_instantiations+1, column=0)
        probability_entry.grid(row=self.shown_instantiations+1, column=1)
        self.instantiations.append((name_entry, probability_entry))
        self.shown_instantiations += 1

    def validate(self):
        """
        highlights empty fields

        Returns:
            bool:
                True if the entries are not empty
        """
        # TODO: entries cannot be the same (len(entries) must be the same as len(set(entries.get())))
        empty_entries = []
        self.context_entry.configure(highlightbackground='black',
                                     selectbackground='black', highlightcolor='black')
        if not self.context_entry.get():
            empty_entries.append(self.context_entry)
        for instantiation in self.instantiations:
            for entry in instantiation:
                entry.configure(highlightbackground='black',
                                selectbackground='black', highlightcolor='black')
                if not entry.get():
                    empty_entries.append(entry)
        if empty_entries:
            # mark red
            for entry in empty_entries:
                entry.configure(highlightbackground='red',
                                selectbackground='red', highlightcolor='red')
            return False
        else:
            return True

    def apply(self):
        """
        Applies the result to hand it over to the master
        """
        self.result = defaultdict(lambda: defaultdict(dict))
        for instantiation in self.instantiations:
            self.result[self.context_entry.get(
            )][instantiation[0].get()] = float(instantiation[1].get())


class Configurator(tk.Tk):
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
        tk.Tk.__init__(self, *args, **kwargs)
        self.setup_layout()
        self.bayesNet = BayesNet(config)
        self.create_fields()
        self.title("Context Based Intention Recognition Configurator")

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
        self.fill_advanced_table()

    def set_decision_threshold(self):
        """
        This sets value in the decision threshold entry from the config
        """
        self.decision_string_value.set(
            self.bayesNet.config['decision_threshold'])

    def adjust_button_visibility(self):
        """
        Adjusts if buttons are visible or not.

        Buttons for edit and delete will only be visible if there is a corresponding intention or context already created.
        """
        if self.bayesNet.config['contexts']:
            # set visible
            self.edit_context_button.grid()
            self.delete_context_button.grid()
        else:
            self.edit_context_button.grid_remove()
            self.delete_context_button.grid_remove()
        if self.bayesNet.config['intentions']:
            # set visible
            self.edit_intention_button.grid()
            self.delete_intention_button.grid()
        else:
            self.edit_intention_button.grid_remove()
            self.delete_intention_button.grid_remove()

    def new_context(self):
        """
        Open a new Dialog to create new contexts.
        """
        # remove errorText
        self.error_label['text'] = f""
        # open small dialog to create context
        dialog = NewContextDialog(self, title="New Context")
        if dialog.result:
            # check if context already exists!
            # it's always only one new context
            new_context = list(dialog.result.keys())[0]
            try:
                self.bayesNet.add_context(
                    new_context, dialog.result[new_context])
            except AssertionError as e:
                self.error_label['text'] = f"{e}"
            # update view!
            self.create_fields()
            self.context_selection.set(new_context)
            # Explicit call is neccessary because set seems not to trigger the callback
            self.context_selected(new_context)

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
        self.error_label['text'] = f""
        # open small dialog to create context
        context = self.context_selection.get()
        instantiations = self.bayesNet.config['contexts'][context]
        dialog = NewContextDialog(self, title="Edit Context", predefined_context={
                                  context: instantiations})

        if dialog.result:
            try:
                # it's always only one new context
                new_context_name = list(dialog.result.keys())[0]
                new_instantiations = dialog.result[new_context_name]
                self.bayesNet.edit_context(
                    context, new_instantiations, new_context_name)
            except AssertionError as e:
                self.error_label['text'] = f"{e}"
            self.create_fields()
            self.context_selection.set(new_context_name)
            # Explicit call is neccessary because set seems not to trigger the callback
            self.context_selected(new_context_name)

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

    def onclicked_advanced(self, e):
        """
        Un/folds the advanced section
        """
        if self.advanced_folded:
            self.advanced_label.config(text=u'advanced \u25B2')
            self.advanced_folded = False
            self.advanced_hidden_frame.grid()
        else:
            self.advanced_label.config(text=u'advanced \u25BC')
            self.advanced_folded = True
            self.advanced_hidden_frame.grid_forget()

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
        self.advanced_table.grid_forget()
        self.advanced_table.destroy()

        self.advanced_table = tk.Frame(self.advanced_hidden_frame)
        self.advanced_table.grid(row=0, column=0)
        tk.Label(self.advanced_table, text='Intention').grid(row=0, column=0)
        tk.Label(self.advanced_table, text='|').grid(row=0, column=1)
        tk.Label(self.advanced_table, text='Contexts').grid(row=0, column=2)
        tk.Label(self.advanced_table, text='|').grid(row=0, column=3)
        tk.Label(self.advanced_table, text='Influence Value').grid(
            row=0, column=4)
        row = 1
        for intention, context_influence in self.bayesNet.config['intentions'].items():
            # print(context_influence)
            for context in context_influence:
                # print(context)
                if isinstance(context, tuple):
                    # print(len(list(context_influence[context])))
                    for j in range(len(list(context_influence[context]))):
                        key = (list(context_influence[context])[j])
                        # For every combined case make a label and a button
                        tk.Label(self.advanced_table, text=f'{intention}').grid(
                            row=row, column=0)
                        tk.Label(self.advanced_table, text='|').grid(
                            row=row, column=1)
                        # build context String
                        context_string = ""
                        for i, _context in enumerate(context):
                            # print(key[i])
                            context_string += f'{_context}={str(key[i])}, '
                        context_string = context_string[:-2]
                        # print(_context)
                        # print(context_string)
                        tk.Label(self.advanced_table, text=context_string).grid(
                            row=row, column=2)
                        tk.Label(self.advanced_table, text='|').grid(
                            row=row, column=3)
                        tk.Label(self.advanced_table, text=f'{list(context_influence[context].values())[0]}').grid(
                            row=row, column=4)
                        tk.Button(self.advanced_table, text='remove', command=lambda intention=intention, contexts=context, instantiations=list(context_influence[context].keys())[0]: self.remove_combined_influence(
                            intention, contexts, instantiations)).grid(row=row, column=5)
                        row += 1
                        # print(self.advanced_new_button)
                        # print("test")
                        # print(context_string)

    def remove_combined_influence(self, intention: str, contexts: tuple, instantiations: tuple):
        self.bayesNet.del_combined_influence(
            intention, contexts, instantiations)
        self.fill_advanced_table()

    def setup_layout(self):
        """
        Setting up the layout of the GUI.
        """
        ###### Context ######
        self.context_label_frame = tk.Frame(self)
        self.context_label_frame.grid(row=0, column=0)
        tk.Label(self.context_label_frame,
                 text='Apriori Probability for ').grid(row=0, column=0)
        self.context_selection = tk.StringVar(
            self.context_label_frame, 'Context')
        values = []
        self.context_dropdown = tk.OptionMenu(
            self.context_label_frame, self.context_selection, *values, command=self.context_selected, value=self.context_selection.get())
        self.context_dropdown.grid(row=0, column=1)

        self.edit_context_button = tk.Button(self.context_label_frame,
                                             command=self.edit_context, text='Edit')
        self.edit_context_button.grid(row=0, column=2)

        self.delete_context_button = tk.Button(self.context_label_frame,
                                               command=self.delete_context, text='Delete')
        self.delete_context_button.grid(row=0, column=3)

        self.new_context_button = tk.Button(self.context_label_frame,
                                            command=self.new_context, text='New Context')
        self.new_context_button.grid(row=0, column=4)

        self.context_frame = tk.Frame(self)
        self.context_frame.grid(row=1, column=0, columnspan=3)
        self.context_instantiations = defaultdict(dict)

        ##### Intention ####
        self.intention_label_frame = tk.Frame(self)
        self.intention_label_frame.grid(row=2, column=0)
        tk.Label(self.intention_label_frame,
                 text='Influence of ').grid(row=0, column=0)
        self.influencing_context_selection = tk.StringVar(
            self.intention_label_frame, 'Context')
        values = []
        self.influencing_context_dropdown = tk.OptionMenu(
            self.intention_label_frame, self.influencing_context_selection, *values, command=self.influencing_context_selected, value=self.influencing_context_selection.get())
        self.influencing_context_dropdown.grid(row=0, column=1)

        tk.Label(self.intention_label_frame, text=' on ').grid(row=0, column=2)
        self.intention_selection = tk.StringVar(
            self.intention_label_frame, 'Intention')
        values = []
        self.intention_dropdown = tk.OptionMenu(
            self.intention_label_frame, self.intention_selection, *values, command=self.influencing_context_selected, value=self.intention_selection.get())
        self.intention_dropdown.grid(row=0, column=3)

        self.edit_intention_button = tk.Button(self.intention_label_frame,
                                               command=self.edit_intention, text='Edit')
        self.edit_intention_button.grid(row=0, column=4)

        self.delete_intention_button = tk.Button(self.intention_label_frame,
                                                 command=self.delete_intention, text='Delete')
        self.delete_intention_button.grid(row=0, column=5)

        self.new_intention_button = tk.Button(self.intention_label_frame,
                                              command=self.new_intention, text='New Intention')
        self.new_intention_button.grid(row=0, column=6)
        self.intention_frame = tk.Frame(self)
        self.intention_frame.grid(row=3, column=0)
        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))

        ### Decision Threshold ###
        self.decision_frame = tk.Frame(self)
        self.decision_frame.grid(row=4, column=0)
        decision_label = tk.Label(
            self.decision_frame, text='Decision Threshold: ')
        self.decision_string_value = tk.StringVar(
            self.decision_frame)
        self.decision_string_value.trace_add(
            mode="write", callback=lambda *args: self.decision_threshold_changed(*args))
        self.decision_entry = tk.Entry(
            self.decision_frame, textvariable=self.decision_string_value)
        decision_label.grid(row=0, column=0)
        self.decision_entry.grid(row=0, column=1)

        #### Advanced ####
        self.advanced_frame = tk.Frame(self)
        self.advanced_frame.grid(row=5, column=0)
        self.advanced_label = tk.Label(
            self.advanced_frame, text=u'advanced \u25BC')
        self.advanced_folded = True
        self.advanced_label.grid(row=0, column=0)
        self.advanced_label.bind("<Button-1>", self.onclicked_advanced)
        self.advanced_hidden_frame = tk.Frame(self.advanced_frame)
        self.advanced_hidden_frame.grid(row=1, column=0)
        self.advanced_table = tk.Frame(self.advanced_hidden_frame)
        self.advanced_table.grid(row=0, column=0)

        self.advanced_new_button = tk.Button(
            self.advanced_hidden_frame, command=self.new_combined_influence, text='new combined context influence')
        self.advanced_new_button.grid(row=1, column=0)
        self.advanced_hidden_frame.grid_forget()

        #### Load & Save #####
        self.load_save_frame = tk.Frame(self)
        self.load_save_frame.grid(row=6, column=0)
        self.load_button = tk.Button(self.load_save_frame,
                                     command=self.load, text='Load')
        self.load_button.grid(row=0, column=0)
        self.save_button = tk.Button(self.load_save_frame,
                                     command=self.save, text='Save')
        self.save_button.grid(row=0, column=1)

        #### Error Area #######
        self.error_frame = tk.Frame(self)
        self.error_frame.grid(row=7, column=0)
        self.error_label = tk.Label(self.error_frame, fg='#f00')
        self.error_label.pack()

    def decision_threshold_changed(self, *args):
        """
        Callback for change of the decision threshold.
        """
        self.error_label['text'] = f""
        try:
            self.bayesNet.change_decision_threshold(
                float(self.decision_string_value.get()))
        except AssertionError as e:
            self.error_label['text'] = f"{e}"
        except ValueError as e:
            self.error_label['text'] = f'Decision Threshold must be a number'

    def set_context_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for a context optionMenu with the options and the corresponding command.

        Args:
            options: A list containing the options in the context dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.context_selected
        self.context_dropdown.destroy()
        if options:
            self.context_selection.set(
                list(options)[0] if options else 'Context')
            self.context_dropdown = tk.OptionMenu(
                self.context_label_frame, self.context_selection, *options, command=command)
        else:  # clear
            self.context_selection = tk.StringVar(
                self.context_label_frame, 'Context')
            values = []
            self.context_dropdown = tk.OptionMenu(
                self.context_label_frame, self.context_selection, *values, command=command, value=self.context_selection.get())
        self.context_dropdown.grid(row=0, column=1)
        command(self.context_selection.get())

    def set_influencing_context_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for the influencing context optionMenu with the options and the corresponding command.

        Args:
            options: A list containing the options in the influencing context dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.influencing_context_selected
        self.influencing_context_dropdown.destroy()
        if options:
            self.influencing_context_selection.set(
                list(options)[0] if options else 'Context')
            self.influencing_context_dropdown = tk.OptionMenu(
                self.intention_label_frame, self.influencing_context_selection, *options, command=command)
        else:  # clear
            self.influencing_context_selection = tk.StringVar(
                self.intention_label_frame, 'Context')
            values = []
            self.influencing_context_dropdown = tk.OptionMenu(
                self.intention_label_frame, self.influencing_context_selection, *values, command=command, value=self.influencing_context_selection.get())
        self.influencing_context_dropdown.grid(row=0, column=1)
        command(self.influencing_context_selection.get())

    def set_intention_dropdown(self, options: list, command: function = None):
        '''
        This sets the options for a intention optionMenu with the options and the corresponding command

        Args:
            options: A list containing the options in the intention dropdown
            command: a function which will be triggered when clicked on the dropdown option
        '''
        if not command:
            command = self.influencing_context_selected
        self.intention_dropdown.destroy()
        if options:
            self.intention_selection.set(
                list(options)[0] if options else 'Intention')
            self.intention_dropdown = tk.OptionMenu(
                self.intention_label_frame, self.intention_selection, *options, command=command)
        else:  # clear
            self.intention_selection = tk.StringVar(
                self.intention_label_frame, 'Intention')
            values = []
            self.intention_dropdown = tk.OptionMenu(
                self.intention_label_frame, self.intention_selection, *values, command=command, value=self.intention_selection.get())
        self.intention_dropdown.grid(row=0, column=3)
        command(self.intention_selection.get())

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
                        widget.destroy()
                    except AttributeError:
                        pass  # can not destroy StringVars
                    except Exception as e:
                        # TODO: better logging
                        print(f"couldn't destroy: {e}")

        self.context_instantiations = defaultdict(dict)
        row = 0
        if context not in self.bayesNet.config['contexts']:
            return
        config = self.bayesNet.config
        for instantiation, value in config['contexts'][context].items():
            instantiation_label = tk.Label(self.context_frame,
                                           text=f'{instantiation}: ')
            instantiation_label.grid(row=row, column=0)

            string_value = tk.StringVar(
                self.context_frame, value=str(value))
            string_value.trace_add(mode="write", callback=lambda *args, context=context,
                                   instantiation=instantiation: self.apriori_values_changed(*args, context=context, instantiation=instantiation))

            entry = tk.Entry(self.context_frame, textvariable=string_value)
            entry.grid(row=row, column=1)

            self.context_instantiations[context][instantiation] = (
                instantiation_label,
                entry,
                string_value
            )
            row += 1

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
                            widget.destroy()
                        except AttributeError:
                            pass  # can not destroy StringVars
                        except Exception as e:
                            # TODO: better logging
                            print(f"couldn't destroy: {e}")
        intention = self.intention_selection.get()
        context = self.influencing_context_selection.get()
        if context not in self.bayesNet.config['contexts'] or intention not in self.bayesNet.config['intentions']:
            return

        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))
        row = 0
        for instantiation, value in self.bayesNet.config['intentions'][intention][context].items():
            instantiation_label = tk.Label(self.intention_frame,
                                           text=f'Influence of {context}:{instantiation} on {intention}: LOW ')
            instantiation_label.grid(row=row, column=0)

            slider = tk.Scale(self.intention_frame, from_=0, to=5, tickinterval=1, variable=tk.IntVar(self.intention_frame, value),
                              orient=tk.HORIZONTAL, command=lambda value, context=context, intention=intention, instantiation=instantiation: self.influence_values_changed(value, context, intention, instantiation))
            slider.grid(row=row, column=1)

            high_label = tk.Label(self.intention_frame,
                                  text=f' HIGH')
            high_label.grid(row=row, column=2)

            self.intention_instantiations[intention][context][instantiation] = (
                instantiation_label,
                slider,
                high_label,
            )
            row += 1

    def load(self):
        """
        opens a askopenfilename dialog to load a config
        """
        # open file selector
        filetypes = (
            ('yaml files', '*.yml'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(title='Choose Config',
                                      filetypes=filetypes)
        # set config
        # try-except to write error if config not valid
        try:
            self.error_label['text'] = 'loading BayesNet...'
            self.bayesNet.load(filename)
            self.error_label['text'] = ''
        except AssertionError as e:
            # show Exception text in designated area
            self.error_label['text'] = f"couldn't load {filename}:\n{e}"
        self.create_fields()

    def save(self):
        """
        opens a asksaveasfilename dialog to save a config
        """
        filetypes = (
            ('yaml files', '*.yml'),
            ('All files', '*.*')
        )
        # try:
        save_filepath = fd.asksaveasfilename(
            title='Save Config', defaultextension='.yml', filetypes=filetypes)
        if save_filepath:
            # TODO. how to handle saving invalid config?
            self.bayesNet.save(save_filepath)

    def apriori_values_changed(self, *args, context, instantiation):
        """
        Callback for change of the apriori values.

        Args:
            context: name of the context
            instantiation: name of the corresponding instantiation
        """
        # update config
        self.error_label['text'] = f""
        try:
            self.bayesNet.change_context_apriori_value(context=context, instantiation=instantiation, value=float(
                self.context_instantiations[context][instantiation][2].get()))
        except AssertionError as e:
            self.error_label['text'] = f"{e}"
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
        self.error_label['text'] = f""
        try:
            self.bayesNet.change_influence_value(
                intention=intention, context=context, instantiation=instantiation, value=int(value))
        except AssertionError as e:
            self.error_label['text'] = f"{e}"
