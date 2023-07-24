""" 
This module provides a class for a two-layer graph for context based intention recognition.
"""
# System imports
import itertools
from copy import deepcopy

# 3rd party imports
import pyqtgraph as pg
import numpy as np
from PyQt5.QtGui import QColor


class TwoLayerGraph(pg.GraphItem):
    """
    Graph Visualization for the two layer bayesian network
    """

    def __init__(self, dist=10, size=3, line_width=[0, 25], pxMode=False, **kwds):
        """
        Initialize the TwoLayerGraph.

        Args:
            dist (int): The distance parameter.
            size (int): The size parameter.
            line_width (list): A list representing the line width.
            pxMode (bool): A flag indicating whether the pxMode is enabled or not.
            **kwds: Additional keyword arguments to be passed.

        """
        super().__init__(**kwds)
        self.dist = dist
        self.size = size
        self.line_width = line_width
        self.pxMode = pxMode
        self.unfolded_context = set()
        self.textItems = []
        # TODO: [Refactoring update config] this is missleading - The graph does not only have one context and one intention!
        self.context = None
        self.intention = None

    def _set_pos(self):
        """
        Add all the data points in the pos array
        """
        i = 0
        j = 0
        added_context = set()
        for intention, context_dict in self.config['intentions'].items():
            position = (self.dist, self.dist / 2 + (j * self.dist))
            self.data["pos"].append(position)
            self.data["names"].append(intention)
            self.data["intention_indices"].append(i)
            # self.data["mapping"][position] = intention
            i += 1
            j += 1
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
                        position = (0, i * self.dist)
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

    # TODO: [Refactoring update config] why are we doing this? On slider movement the config should be updated and then it should just normally redraw
    def update_value(self, context, intention):
        """
        Gets the values from configurator when slider is modified by the user 
        """
        self.context = context
        self.intention = intention
        self.set_config(self.config)

    def _set_pen(self):
        """
        Add all the pens for the connections in the pen array 
        """
        start_color = QColor(255, 0, 0)  # Start color (e.g., red)
        end_color = QColor(0, 255, 0)  # End color (e.g., green)

        def calculate_color(normalized_mean):
            """
            To calculate color value
            """
            red = start_color.red() + normalized_mean * (end_color.red() - start_color.red())
            green = start_color.green() + normalized_mean * \
                (end_color.green() - start_color.green())
            blue = start_color.blue() + normalized_mean * \
                (end_color.blue() - start_color.blue())
            return red, green, blue

        def calculate_width(normalized_mean):
            """
            To calculate the width
            """
            return self.line_width[0] + (self.line_width[1] - self.line_width[0]) * normalized_mean

        def calculate_normalized_mean(context, intention):
            """
            To calculate the normalized mean
            """
            values = list(self.config["intentions"]
                          [intention][context].values())
            return np.mean(values) / 5.0

        for start, end in self.data["adj"]:
            if start in self.data["context_indices"] or start in self.data["instantiation_indices"]:
                context = self.data["names"][start]
                intention = self.data["names"][end]
            else:
                context = self.data["names"][end]
                intention = self.data["names"][start]

            color = pg.mkPen().color()

            if start in self.data["instantiation_indices"]:
                # Hack: TODO: this is problematic if the context has a colon in name
                context, instantiation = self.data["names"][start]
                # TODO. problem with default dict or problem with type - for "human holding object" bool is used and it does not work...
                normalized_mean = self.config["intentions"][intention][context][instantiation] / 5.0
            else:
                normalized_mean = calculate_normalized_mean(context, intention)

            alpha = color.alpha()
            red, green, blue = calculate_color(normalized_mean)
            width = calculate_width(normalized_mean)

            self.data["pen"].append(np.array([(red, green, blue, alpha, width)], dtype=[
                ('red', np.uint8), ('green', np.uint8), ('blue', np.uint8), ('alpha', np.uint8), ('width', np.uint8)]))

        # TODO: [Refactoring update config] This should not be a special case!
        if self.context or self.intention is not None:
            context = self.context
            intention = self.intention
            normalized_mean = calculate_normalized_mean(context, intention)
            color_values = self.data['pen'][0][0]
            if self.data["names"][start] == context and self.data["names"][end] == intention:
                red = color_values[0]
                green = color_values[1]
                blue = color_values[2]
                red, green, blue = calculate_color(normalized_mean)

            width = calculate_width(normalized_mean)
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
            self.textItems.append(text_item)

    def set_config(self, config):
        """
        Uses the config to set the data and draws the graph
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
