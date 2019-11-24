from observer import Observable
from configurations import *
import math
from PIL import Image
import numpy as np


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
        - хранить изображение интерферограммы
        - хранить изображение в виде numpy матрицы
        - получать numpy матрицу целиком
        - получать rgba пикселя
        - получать любой канал пикселя (1 -r, 2 - g и тд)
    """
    __image = 0
    __NpImage = 0

    def set_image(self, s):
        self.__image = Image.open(s)
        self.__NpImage = np.asarray(self.__image)

    def get_image_npmatrix(self):
        return self.__NpImage

    def get_canal_pixel(self, x, y, c):
        return self.__NpImage[x, y, c]

    def get_rgb_pixel(self, x, y):
        return self.__NpImage[x, y]


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