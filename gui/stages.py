from dataclasses import dataclass
from typing import Any

from docstring_parser import parse
from PySide6 import QtCore

from monkey_callbacks import *
from monkey_visualizers import *


@dataclass
class SettingsItem:
    text: str       # Human-readable name
    arg_name: str   # Name of argument for function
    type: Any       # Either type text (bool, int etc.) or range
    value: Any      # Should be initially set to default


class Stage(QtCore.QObject):
    ready_signal = QtCore.Signal()

    def __init__(self, stage_number, callback, visualizer, input_data=None):
        super().__init__()
        self.number = stage_number
        self.callback = callback
        self.visualizer = visualizer
        self.input_data = input_data
        self.result = None
        self.is_run = False

        # Parse settings
        doc = parse(callback.__doc__)
        self.name = doc.short_description

        self.settings = []
        arg_names = {p.arg_name: p.description for p in doc.params}
        for i, (arg, arg_type) in enumerate(callback.__annotations__.items()):
            if arg in arg_names:
                s = SettingsItem(arg_names[arg], arg, arg_type, callback.__defaults__[i])
                self.settings.append(s)

    def proceed(self):
        kwargs = {s.arg_name: s.value for s in self.settings}
        self.result = self.callback(self.input_data, **kwargs)
        self.ready_signal.emit()

    def copy(self):
        return self.__class__(self.number, self.callback, self.input_data)


functions = [get_base_points, trace_interference_lines, calculate_phases]
visualizers = [visualize_base_points, visualize_interference_lines, visualize_phases]

stages = [Stage(i, f, v) for i, (f, v) in enumerate(zip(functions, visualizers))]
