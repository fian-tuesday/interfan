from observer import Observable
from configurations import *
import math
from PIL import Image, ImageTk
import numpy as np


class InterferogramModel:
    """ Contains the data of the interferogram.
        Can:
        - store the image of the interferogram
        - store image as numpy matrix
        - get the whole numpy matrix
        - get rgb pixel
        - get any channel of the pixel (0-r, 1 - g and so on)
        - get green section
        - get width and height of image
    """
    __image = 0
    __NpImage = 0
    __prepimage = "interferogram.tif"

    def set_image(self, s):
        self.__image = Image.open(s)
        self.__prepimage = ImageTk.PhotoImage(Image.open(s))
        self.__NpImage = np.asarray(self.__image)

    def open_image(self):
        return self.__prepimage

    def prepared_image(self):
        return ImageTk.PhotoImage(self.__image)

    def get_image_npmatrix(self):
        return self.__NpImage

    def get_canal_pixel(self, y, x, c):
        return self.__NpImage[y, x, c]

    def get_rgb_pixel(self, y, x):
        return self.__NpImage[y, x]

    def get_green_section(self, x):
        return self.__NpImage[:, x, 1]

    def get_width(self):
        return self.__NpImage.shape[1]

    def get_height(self):
        return self.__NpImage.shape[0]


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