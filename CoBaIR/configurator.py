'''
This module is a GUI configurator to create configurations for context based intention recognition - it can as well be used in a live mode to test the configuration
'''

# System imports
from collections import defaultdict
import tkinter as tk
from tkinter import StringVar, filedialog as fd
from tkinter.simpledialog import Dialog
from threading import Timer
from copy import deepcopy
import traceback
from types import FunctionType as function

import yaml
# 3rd party imports

# local imports
from .bayes_net import BayesNet, load_config

# end file header
__author__ = 'Adrian Lubitz'


class NewIntentionDialog(Dialog):
    """Dialog Window for new Intention"""

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


class NewContextDialog(Dialog):
    """Dialog Window for new Context"""

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
        tk.Label(name_frame, text="New Context:").grid(row=0)
        self.context_entry = tk.Entry(name_frame)
        self.context_entry.grid(row=0, column=1)

        # frame for instantiations
        self.instantiations_frame = tk.Frame(master)
        self.instantiations_frame.grid(row=1)
        tk.Label(self.instantiations_frame,
                 text="Instantiation Name").grid(row=0)
        tk.Label(self.instantiations_frame,
                 text="Apriori Probability").grid(row=0, column=1)
        self.instantiations = []
        self.shown_instantiations = 1
        while(self.shown_instantiations < 3):
            # tk.Label(self.instantiations_frame,
            #          text=f"Instantiation {self.shown_instantiations}:").grid(row=self.shown_instantiations)
            name_entry = tk.Entry(self.instantiations_frame)
            probability_entry = tk.Entry(self.instantiations_frame)
            name_entry.grid(row=self.shown_instantiations, column=0)
            probability_entry.grid(row=self.shown_instantiations, column=1)
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
        name_entry.grid(row=self.shown_instantiations, column=0)
        probability_entry.grid(row=self.shown_instantiations, column=1)
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
        # initialization of the timer
        # self.change_timer = Timer(1, self._update_bayes_net)

        self.bayesNet = BayesNet()
        # This will only be used for the case where you defined context or intention  before the other exists
        # self.tmp_config = config
        # if not self.tmp_config:
        #     self.tmp_config = defaultdict(
        #         lambda: defaultdict(lambda: defaultdict(dict)))
        # if self.tmp_config:
        #     self._update_bayes_net()

        self.title("Context Based Intention Recognition Configurator")

    def create_fields(self):
        """
        Creates all necessary fields in the GUI
        """

        self.set_context_dropdown(self.bayesNet.config['contexts'].keys())

        self.set_influencing_context_dropdown(
            self.bayesNet.config['contexts'].keys())

        self.set_intention_dropdown(self.bayesNet.config['intentions'].keys())

    def new_context(self):
        """
        Open a new Dialog to create new contexts.
        """
        # remove errorText
        self.error_label['text'] = f""
        # open small dialog to create context
        dialog = NewContextDialog(self, title="New Context")
        # it's always only one new context
        if dialog.result:
            # check if context already exists!
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

    def setup_layout(self):
        """
        Setting up the layout of the GUI.
        """
        ###### Context ######
        # TODO: remove/edit context or instantiation
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
        self.new_context_button = tk.Button(self.context_label_frame,
                                            command=self.new_context, text='New Context')
        self.new_context_button.grid(row=0, column=2)

        self.context_frame = tk.Frame(self)
        self.context_frame.grid(row=1, column=0, columnspan=3)
        self.context_instantiations = defaultdict(dict)

        ##### Intention ####
        # TODO: remove/edit intention
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

        self.new_intention_button = tk.Button(self.intention_label_frame,
                                              command=self.new_intention, text='New Intention')
        self.new_intention_button.grid(row=0, column=4)
        self.intention_frame = tk.Frame(self)
        self.intention_frame.grid(row=3, column=0)
        self.intention_instantiations = defaultdict(lambda: defaultdict(dict))

        #### Load & Save #####
        self.load_save_frame = tk.Frame(self)
        self.load_save_frame.grid(row=4, column=0)
        self.load_button = tk.Button(self.load_save_frame,
                                     command=self.load, text='Load')
        self.load_button.grid(row=0, column=0)
        self.save_button = tk.Button(self.load_save_frame,
                                     command=self.save, text='Save')
        self.save_button.grid(row=0, column=1)

        #### Error Area #######
        self.error_frame = tk.Frame(self)
        self.error_frame.grid(row=5, column=0)
        self.error_label = tk.Label(self.error_frame, fg='#f00')
        self.error_label.pack()

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
            print(f"options: {options}")
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
                    except Exception as e:
                        print(f"couldn't destroy: {e}")

        self.context_instantiations = defaultdict(dict)
        row = 0
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
                        except Exception as e:
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
