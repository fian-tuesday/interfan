""" === Контроллеры  ===
В этом файле содержатся обработчики событий для виджетов:
- анализатора,
- интерферограммы
- базовых точек,
- интерференционных линий
"""
from interfan_model import *
from interfan_view import *


class MultilayerWorkspaceControl:
    """ Содержит обработчики сигналов от пользователя, относящиеся к анализатору.
        Возможности:
        - редактирование базовых точек (удаление левой кнопкой мыши, добавление правой и средней)
        - редактирование интерференционных линий
    """
    def __init__(self, view: "MultilayerWorkspace"):
        self._view = view

    def load_interferogram(self, filename):
        print("Типа загружаем интерферограмму: ", filename)
        self.model.interferogram.set_image(filename)
        pass

    def save_phases(self, filename):
        print("Типа сохраняем фазы: ", filename)
        pass


class InterferogramControl:
    """ Обработчик событий для интерферограммы.
        Пока будет пустым. Планируется, что в будущем за неё можно будет тягать мышкой.
    """
    def __init__(self, model: InterferogramModel):
        self.model = model


class BasePointsControl:
    """ Обработчик событий для базовых точек. """
    def __init__(self, model: BasePointsModel):
        self.model = model


class LinesControl:
    """ Обработчик событий для интерференционных линий. """
    def __init__(self, model: LinesModel):
        self.model = model
