from dataclasses import dataclass
from typing import Any

from docstring_parser import parse
import numpy as np
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
    ready_signal = QtCore.Signal(int)

    def __init__(self, stage_number, callback, visualizer, input_data=None):
        super().__init__()
        self.number = stage_number
        self.callback = callback
        self.visualizer = visualizer
        self.input_data = input_data
        self.result = None
        self.image = None
        self.is_run = False

        # Parse settings
        doc = parse(callback.__doc__)
        self.name = doc.short_description

        self.settings = []
        for p in doc.params:
            if p.description != 'input_data':
                try:
                    _type = eval(p.type_name)
                except SyntaxError:
                    raise TypeError(f'invalid type name for {p.arg_name}: {p.type_name}')
                try:
                    default = eval(p.default)
                except SyntaxError:
                    raise TypeError(f'invalid default value for {p.arg_name}: {p.default}')
                s = SettingsItem(p.description, p.arg_name, _type, default)
                self.settings.append(s)

    def __repr__(self):
        return f'Stage <{self.number}: {self.name}>\n' \
               f'Settings: {self.settings}'

    def proceed(self):
        kwargs = {s.arg_name: s.value for s in self.settings}
        self.result = self.callback(self.input_data, **kwargs)
        print(f'{self.name} emitting signal')
        self.ready_signal.emit(self.number)

    def visualize_result(self, input_image):
        self.image = self.visualizer(input_image, self.result)

    def copy(self):
        return self.__class__(self.number, self.callback, self.input_data)


def load_image(input_image_filename):
    """
    Загрузка файла
    """
    input_image = Image.open(input_image_filename)
    image_data = input_image.getdata()
    # Зелёный в данной картинке всегда средний по яркости - берём именно его
    return np.array(list(components[1] for components in image_data)).reshape(input_image.size[::-1])


def visualize_image(input_image, brightness_array):
    return Image.fromarray(brightness_array)


functions = [get_base_points, trace_interference_lines, calculate_phases]
visualizers = [visualize_base_points, visualize_interference_lines, visualize_phases]

first_stage = Stage(0, load_image, visualize_image)

stages = [first_stage] + [Stage(i, f, v) for i, (f, v) in enumerate(zip(functions, visualizers), 1)]

if __name__ == '__main__':
    from _closed.functions import get_base_points
    print(parse(get_base_points.__doc__))
    print(Stage(1, get_base_points, print))
