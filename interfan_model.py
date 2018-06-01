from observer import Observable
from configurations import *
import math
#import numpy


# === Модель ===
class AnalyzerModel:
    """ Главный аналитический объект. Вся рабочая математика содержится тут.
        Инкапсулирует объекты:
        - модель интерферограммы
        - модель базовых точек
        - модель линий
        - модель фазовой картинки

        Осуществляет взаимодействие объектов.
        Умеет:
        - находить базовые точки по данным интерферограммы
        - трассировать интерференционные линии по базовым точкам
    """
    def __init__(self):
        self.interferogram = InterferogramModel()
        self.base_points = BasePointsModel()
        self.lines = LinesModel()

    def locate_base_points(self):
        """ Находит базовые точки по данным интерферограммы
            работает по вертикальным срезам, для точек в диапазоне
            для параболы критерию хи-квадрат
        """
        pass


class InterferogramModel:
    """ Содержит данные интерферограммы.
        Умеет:
        -
    """
    pass

class BasePointsModel(Observable):
    """ Содержит данные базовых точек.
        Умеет:
        - сохранять их в файл
        - читать из файла
        - добавлять базовую точку
        - удалять базовую точку
    """
    def some_method(self):
        self.notify_observers("СООБЩЕНИЕ!!!")


class LinesModel(Observable):
    """ Содержит данные интерференционных линий в виде последовательности точек Point(x, y).
        Умеет:
        - сохранять их в файл
        - читать из файла
        - перемещать точку в заданной линии
        - добавлять точку в середину отрезка заданной линии
        - для заданного номера линии и заданной координаты x возвращать
    """
    pass


class PhasesModel(Observable):
    """ Содержит данные фазовой картинки
        Умеет:
        - сохранять её в файл
        - читать её из файла
    """
    pass