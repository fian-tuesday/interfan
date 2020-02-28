from observer import Observable
from configurations import *
import math
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from abc import ABC, abstractmethod
from ctypes import *
import os
from numpy.core._multiarray_umath import ndarray

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

class Tracer:

    """
        This class contains information about traced lines.
        Lines are stored as a one-dimensional array. It consists of a sequence of base points,
        the remainder of the division of the element number by the width of the image is the abcissa of the point,
        the value of the element is its ordinate.
        The class can return the number of lines, an array of base points, and draw lines on the original image.
    """

    def __init__(self, matrix, full_path_to_shared_library):
        matrix = matrix.transpose()
        self._lib = CDLL(full_path_to_shared_library)
        self._width = matrix.shape[0]
        self._height = matrix.shape[1]
        self._matrix = np.array(matrix)
        self._matrix = self._matrix.astype(np.int32)
        self._amount_lines = 0

    def get_lines(self):
        return self._lines

    def get_amount_lines(self):
        return self._amount_lines

    def draw_lines(self, initional_picture, result_picture):
        image = Image.open(initional_picture)
        array = []
        for i in range(self._amount_lines):
            draw = ImageDraw.Draw(image)
            for j in range(self._width):
                array.append((j, self._lines[i, j]))
            draw.line(array, (255, 255, 255), 1)
            array.clear()
            del draw
        image.save(result_picture, "PNG")

class Tracer1(Tracer):

    """
        Only the last function that performs the trace is required.
        The rest of the functions were needed to check the C code,
            and some may not work (they checked the robotability of the C functions, which were later changed.
        If you need to change the C code, you will need to compile it into a shared file (.so).
            To do this, write the following line in the terminal:
            gcc -shared -fPIC -o Tracer1.so ~/Tracer1.c
        The tracer is not perfect. It has a hardcode (the number of points for averaging,
            the approximate period in pixels, and the required number of lines).
            Later, hardcode will be removed from the code.
    """

    def _draw_array(self, array, flag, input, output):
        if flag == 0:
            image = Image.open(input)
        else:
            image = Image.new("RGB", (self._height, 256), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        result = []
        for i in range(len(array)):
            result.append((i, array[i]))
        draw.line(result, (0, 0, 0), 1)
        del draw
        image.save(output, "PNG")

    def _draw_vertical_lines(self, array, length, input, output):
        img = Image.open(input)
        draw = ImageDraw.Draw(img)
        for i in range(length):
            draw.line([(array[i], 0), (array[i], 255)], (0, 255, 0), 1)
        del draw
        img.save(output, "PNG")

    def _draw_horizontal_lines(self, y, length, input, output):
        img = Image.open(input)
        draw = ImageDraw.Draw(img)
        draw.line([(0, y), (length, y)], (0, 255, 0), 1)
        del draw
        img.save(output, "PNG")

    def _test_int_max(self, nparray, length):
        c_p = POINTER(c_int32)
        nparray = nparray.astype(np.int32)
        self._lib.restypes = c_int
        self._lib.argtypes = c_p, c_int
        x = self._lib.int_max(nparray.ctypes.data_as(c_p), length)
        print(x, max(nparray))

    def _test_int_min(self, nparray, length):
        c_p = POINTER(c_int32)
        nparray = nparray.astype(np.int32)
        self._lib.restypes = c_int
        self._lib.argtypes = c_p, c_int
        x = self._lib.int_min(nparray.ctypes.data_as(c_p), length)
        print(x, min(nparray))

    def _test_double_max(self, nparray, length):
        c_p1 = POINTER(c_double)
        c_p2 = POINTER(c_double)
        nparray = nparray.astype(np.double)
        result = np.array([0.0])
        result = result.astype(np.double)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_p2
        self._lib.double_max(nparray.ctypes.data_as(c_p1), length, result.ctypes.data_as(c_p1))
        print(result[0], max(nparray), length)
        print(nparray)

    def _test_double_min(self, nparray, length):
        c_p1 = POINTER(c_double)
        c_p2 = POINTER(c_int)
        c_p3 = POINTER(c_double)
        nparray = nparray.astype(np.double)
        npnumber = np.array([0])
        npnumber = npnumber.astype(np.int)
        npresult = np.array([0])
        npresult = npresult.astype(np.double)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_p2, c_p3
        self._lib.double_min(nparray.ctypes.data_as(c_p1), length, npnumber.ctypes.data_as(c_p2), npresult.ctypes.data_as(c_p3))
        print(npresult[0], min(nparray))

    def _test_int_array_averaging(self, array):
        length = len(array)
        self._draw_array(array, 1, length, "img1")
        c_p1 = POINTER(c_int32)
        c_p2 = POINTER(c_int32)
        array = array.astype(np.int32)
        average_array = array.astype(np.int32)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_p1, c_p2
        self._lib.int_array_averaging(2, length, array.ctypes.data_as(c_p1), average_array.ctypes.data_as(c_p2))
        self._draw_array(average_array, 1, length,  "img2")

    def _int_array_averaging(self, array, parameter_averaging):
        length = len(array)
        c_p1 = POINTER(c_int32)
        c_p2 = POINTER(c_int32)
        array = array.astype(np.int32)
        average_array = array.astype(np.int32)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_p1, c_p2
        self._lib.int_array_averaging(parameter_averaging, length, array.ctypes.data_as(c_p1), average_array.ctypes.data_as(c_p2))
        return average_array

    def _test_search_minimal_half_period(self, array, length):
        c_p1 = POINTER(c_int32)
        array = array.astype(np.int32)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_int
        period = self._lib.search_minimal_period(array.ctypes.data_as(c_p1), length, 10)
        print("period =", period)

    def _search_minimal_half_period(self, array, length):
        c_p1 = POINTER(c_int32)
        array = array.astype(np.int32)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_int
        period = self._lib.search_minimal_period(array.ctypes.data_as(c_p1), length, 10)
        return period

    def _test_create_array_square_deviation(self, array, parameter):
        length = len(array)
        self.draw_array(array, 1, "img1", "img1")
        c_p1 = POINTER(c_int32)
        c_p2 = POINTER(c_int32)
        array = array.astype(np.int32)
        average_array = array.astype(np.int32)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_p1, c_p2
        self._lib.int_array_averaging(2, length, array.ctypes.data_as(c_p1), average_array.ctypes.data_as(c_p2))
        c_p3 = POINTER(c_double)
        square_deviatios = array.astype(np.double)
        self._lib.restypes = None
        self._lib.argtypes = c_p2, c_int, c_int, c_p3
        self._lib.create_array_square_deviation(average_array.ctypes.data_as(c_p2), length, parameter, square_deviatios.ctypes.data_as(c_p3))
        m = max(square_deviatios)
        for i in range(length):
            square_deviatios[i] = square_deviatios[i] * 256 / m
        self.draw_array(square_deviatios, 1, "input", "output")

    def _create_array_square_deviation(self, array, parameter_averaging, parameter_big_avereging):
        length = len(array)
        average_array = self.int_array_averaging(array, parameter_averaging)
        c_p1 = POINTER(c_double)
        c_p2 = POINTER(c_double)
        square_deviatios = array.astype(np.double)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_int, c_p2
        self._lib.create_array_square_deviation(average_array.ctypes.data_as(c_p1), length, parameter_big_avereging, square_deviatios.ctypes.data_as(c_p2))
        return square_deviatios

    def _rough_search_lows(self, array, parameter_averaging, parameter_big_avereging):
        length = len(array)
        square_deviatios = self.create_array_square_deviation(array, parameter_averaging, parameter_big_avereging)
        period = self.search_minimal_half_period(array, length)
        c_p1 = POINTER(c_double)
        c_p2 = POINTER(c_int32)
        c_p3 = POINTER(c_int)
        rough_mins = array.astype(np.int32)
        amount_rough_mins = np.array([0])
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_int, c_p2, c_p3
        self._lib.rough_search_lows(square_deviatios.ctypes.data_as(c_p1), length, period,
                                    rough_mins.ctypes.data_as(c_p2), amount_rough_mins.ctypes.data_as(c_p3))
        res_rough_mins = np.zeros(amount_rough_mins[0])
        res_rough_mins = res_rough_mins.astype(np.int)
        for i in range(amount_rough_mins[0]):
            res_rough_mins[i] = rough_mins[i]
        return res_rough_mins

    def _test_rough_search_lows(self, array, parameter_averaging, parameter_big_avereging):
        rough_mins = self.rough_search_lows(array, parameter_averaging, parameter_big_avereging)
        amount_rough_mins = len(rough_mins)
        self.draw_vertical_lines(rough_mins, amount_rough_mins, "/home/vladimir/projects_py/img2",
                                 "/home/vladimir/projects_py/rough.png")
        print(rough_mins)
        print(amount_rough_mins)
        print(type(rough_mins[0]))

    def _accurate_search_extremes(self, array, parameter_averaging, parameter_big_avereging):
        average_array = self.int_array_averaging(array, parameter_averaging)
        rough_extrems = self.rough_search_lows(array, parameter_averaging, parameter_big_avereging)
        amount_rough_extrems = rough_extrems.shape[0]
        rough_extrems = rough_extrems.astype(np.int32)
        accurate_extrems = rough_extrems.astype(np.int32)
        c_p1 = POINTER(c_int32)
        c_p2 = POINTER(c_int32)
        c_p3 = POINTER(c_int32)
        self._lib.restypes = c_int
        self._lib.argtypes = c_p1, c_int, c_p2, c_p3
        amount_extrems = self._lib.accurate_search_extremes(rough_extrems.ctypes.data_as(c_p1), amount_rough_extrems,
                                                            average_array.ctypes.data_as(c_p2), accurate_extrems.ctypes.data_as(c_p3))
        amount_extrems = amount_extrems - 1
        result_accurate_extrems = np.zeros(amount_extrems)
        result_accurate_extrems = result_accurate_extrems.astype(np.int)
        for i in range(amount_extrems):
            result_accurate_extrems[i] = accurate_extrems[i]
        return result_accurate_extrems

    def _test_accurate_search_extremes(self, array, parameter_averaging, parameter_big_avereging):
        accurate_extrems = self.accurate_search_extremes(array, parameter_averaging, parameter_big_avereging)
        amount_extrems = len(accurate_extrems)
        self.draw_vertical_lines(accurate_extrems, amount_extrems, "/home/vladimir/projects_py/img2",
                                 "/home/vladimir/projects_py/accurate.png")
        if amount_extrems != 0:
            print(amount_extrems)
            print(accurate_extrems)
        else:
            print("amount of extrems = 0!!!!!!!")

    def _test_load_matrix(self):
        c_p = POINTER(c_int32)
        self._lib.restypes = None
        self._lib.argtypes = c_p, c_int, c_int
        self._lib.test_load(self._matrix.ctypes.data_as(c_p), self._height, self._width)

    def _get_matrix(self):
        return self._matrix

    def trace(self, int_array_parameter, true_amount_lines):
        amount_lines = np.array([0])
        intermediate_lines = np.zeros(self._height * self._height, dtype=np.int16)
        c_p1 = POINTER(c_int32)
        c_p2 = POINTER(c_int16)
        c_p3 = POINTER(c_int32)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_int, c_int, c_int, c_p2, c_p3
        self._lib.trace(self._matrix.ctypes.data_as(c_p1), self._height, self._width, int_array_parameter,
                        true_amount_lines, intermediate_lines.ctypes.data_as(c_p2), amount_lines.ctypes.data_as(c_p3))
        self._amount_lines = amount_lines[0]
        self._lines = np.zeros((self._amount_lines, self._width), dtype=np.int16)
        for i in range(self._amount_lines):
            for j in range(self._width):
                self._lines[i, j] = intermediate_lines[i * self._width + j]

class Base_points:
    '''

     The class stores information about base points in the form
         of two one-dimensional arrays-an abscissa array and an ordinate array.
         Arrays are created from multiple points on each line,
         and each line has the same number of points.
     The class can build new lines on base points using the cubic spline method.
     The class allows you to get and change the coordinates of any base point.

     '''
    def __init__(self, tracer, full_path_to_shared_library, amount_base_points):
        self._tracer = tracer
        self._new_lines = self._tracer.get_lines()
        self._lib = CDLL(full_path_to_shared_library)
        self._amount_base_points = amount_base_points
        self._base_points_y = np.zeros(self._amount_base_points * self._tracer._amount_lines)
        self._base_points_y = self._base_points_y.astype(np.int16)
        self._base_points_x = np.zeros(self._amount_base_points * self._tracer._amount_lines)
        self._base_points_x = self._base_points_x.astype(np.int16)

    def create_base_points_x(self):
        c_p = POINTER(c_int16)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_int, c_p
        self._lib.create_base_points_x(c_int(self._tracer._width), c_int(self._tracer._amount_lines),
                                       c_int(self._amount_base_points), self._base_points_x.ctypes.data_as(c_p))

    def _test_base_points_x(self):
        c_p = POINTER(c_int16)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_int, c_p
        self._lib.test_base_points_x(c_int(self._tracer._width), c_int(self._tracer._amount_lines),
                                     c_int(self._amount_base_points), self._base_points_x.ctypes.data_as(c_p))

    def create_base_points_y(self):
        c_p1 = POINTER(c_int16)
        c_p2 = POINTER(c_int16)
        c_p3 = POINTER(c_int16)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_p2, c_int, c_int, c_int, c_p3
        self._lib.create_base_points_y(self._new_lines.ctypes.data_as(c_p1), self._base_points_x.ctypes.data_as(c_p2),
                                       c_int(self._tracer._width), c_int(self._tracer._amount_lines),
                                       c_int(self._amount_base_points), self._base_points_y.ctypes.data_as(c_p3))

    def _test_base_points_y(self):
        c_p1 = POINTER(c_int16)
        c_p2 = POINTER(c_int16)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_p2, c_int, c_int, c_int
        self._lib.create_base_points_y(self._new_lines.ctypes.data_as(c_p1), self._base_points_x.ctypes.data_as(c_p2),
                                       c_int(self._tracer._width), c_int(self._tracer._amount_lines),
                                       c_int(self._amount_base_points))

    def _load_lines(self, full_path):
        file = open(full_path, "w")

        for i in range(self._tracer._amount_lines):
            for j in range(self._tracer._width):
                s = str(self._new_lines[i, j]) + '\n'
                file.write(s)
        file.close()

    def create_new_lines(self):
        c_p1 = POINTER(c_int16)
        c_p2 = POINTER(c_int16)
        c_p3 = POINTER(c_int16)
        self._lib.restypes = None
        self._lib.argtypes = c_p1, c_int, c_int, c_int, c_p2, c_p3
        self._lib.create_new_lines(self._new_lines.ctypes.data_as(c_p1), c_int(self._tracer._width),
                                   c_int(self._tracer._amount_lines), c_int(self._amount_base_points),
                                   self._base_points_y.ctypes.data_as(c_p2), self._base_points_x.ctypes.data_as(c_p3))

    def get_coordinates_base_point(self, number_line, number_point):
        return (self._base_points_x[number_line * self._amount_base_points + number_point],
                self._base_points_y[number_line * self._amount_base_points + number_point])

    def change_coordinates_point(self, number_line, number_point, new_point):
        border = self.get_border_coordinates_point(number_line, number_point)
        x1 = border[0]
        x2 = border[1]
        x = new_point[0]
        y = new_point[1]
        if (x1 <= x and x <= x2):
            self._base_points_x[number_line * self._amount_base_points + number_point] = x
            self._base_points_y[number_line * self._amount_base_points + number_point] = y
            self.create_new_lines()

    def mark_points(self, initional_picture, result_picture):
        image = Image.open(initional_picture)
        draw = ImageDraw.Draw(image)
        for i in range(self._tracer._amount_lines):
            for j in range(self._amount_base_points):
                x = self._base_points_x[i * self._amount_base_points + j]
                y = self._base_points_y[i * self._amount_base_points + j]
                if x == 0:
                    if y == 0:
                        line1 = [(x, y), (x + 1, y + 1), (x + 2, y + 2)]
                        line2 = []
                    elif y == self._tracer._height - 1:
                        line1 = []
                        line2 = [(x, y), (x + 1, y - 1), (x + 2, y - 2)]
                    else:
                        line1 = [(x, y), (x + 1, y + 1), (x + 2, y + 2)]
                        line2 = [(x, y), (x + 1, y - 1), (x + 2, y - 2)]
                elif x == self._tracer._width - 1:
                    if y == 0:
                        line1 = []
                        line2 = [(x - 2, y + 2), (x - 1, y + 1), (x, y)]
                    elif y == self._tracer._height - 1:
                        line1 = [(x - 2, y - 2), (x - 1, y - 1), (x, y)]
                        line2 = []
                    else:
                        line1 = [(x - 2, y - 2), (x - 1, y - 1), (x, y)]
                        line2 = [(x - 2, y + 2), (x - 1, y + 1), (x, y)]
                else:
                    if y == 0:
                        line1 = []
                        line2 = [(x - 2, y - 2), (x - 1, y - 1), (x, y), (x + 1, y - 1), (x +2, y - 2)]
                    elif y == self._tracer._height - 1:
                        line1 = [(x - 2, y + 2), (x - 1, y + 1), (x, y), (x + 1, y + 1), (x +2, y + 2)]
                        line2 = []
                    else:
                        line1 = [(x - 2, y - 2), (x - 1, y - 1), (x, y), (x + 1, y - 1), (x +2, y - 2)]
                        line2 = [(x - 2, y + 2), (x - 1, y + 1), (x, y), (x + 1, y + 1), (x +2, y + 2)]
                draw.line(line1, (255, 255, 255), 1)
                draw.line(line2, (255, 255, 255), 1)
        del draw
        image.save(result_picture, "PNG")

class Phaser:
    '''

        The class can calculate the phase of each point
            along lines and calculate the difference between two phase patterns
        Also the class can draw the difference phase

    '''
    def __init__(self, unchanged_lines, changed_lines, width, height, amount_lines, full_path_to_shared_library):
        self._unchanged_lines = unchanged_lines
        self._changed_lines = changed_lines
        self._width = width
        self._height = height
        self._amount_lines = amount_lines
        self._unchanged_phase  = np.zeros(width * height)
        self._unchanged_phase = self._unchanged_phase.astype(np.double)
        self._changed_phase  = np.zeros(width * height)
        self._changed_phase = self._changed_phase.astype(np.double)
        self._lib = CDLL(full_path_to_shared_library)
        self._phase_difference = np.zeros(width * height)
        self._phase_difference = self._phase_difference.astype(np.int16)

    def create_unchanged_and_changed_phase(self):
        c_p1 = POINTER(c_int16)
        c_p2 = POINTER(c_double)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_p1, c_int, c_p2
        self._lib.create_phase2(c_int(self._width), c_int(self._height), self._unchanged_lines.ctypes.data_as(c_p1),
                                c_int(self._amount_lines), self._unchanged_phase.ctypes.data_as(c_p2))
        c_p3 = POINTER(c_int16)
        c_p4 = POINTER(c_double)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_p3, c_int, c_p4
        self._lib.create_phase2(c_int(self._width), c_int(self._height), self._changed_lines.ctypes.data_as(c_p3),
                                c_int(self._amount_lines), self._changed_phase.ctypes.data_as(c_p4))

    def _test_create_unchanged_and_changed_phase(self):
        for i in range(self._height):
            for j in range(self._width):
                print(self._changed_phase[i * self._width + j])
            print("***************************************************************")

    def calculate_phase_difference(self):
        c_p1 = POINTER(c_double)
        c_p2 = POINTER(c_double)
        c_p3 = POINTER(c_int16)
        self._lib.restypes = None
        self._lib.argtypes = c_int, c_int, c_p1, c_p2, c_p3
        self._lib.calculate_phase_difference(c_int(self._width), c_int(self._height),
                                             self._unchanged_phase.ctypes.data_as(c_p1),
                                             self._changed_phase.ctypes.data_as(c_p2),
                                             self._phase_difference.ctypes.data_as(c_p3))

    def draw_phase_difference(self, picture):
        image = Image.new("RGB", (self._width, self._height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for i in range(self._width):
            for j in range(self._height):
                collor = self._phase_difference[i * self._height + j]
                draw.point([(i, j)], (collor, collor, collor))
        del draw
        image.save(picture, "PNG")

    def get_phase_difference(self):
        return self._phase_difference

class LinesModel:
    """ Содержит данные интерференционных линий в виде последовательности точек Point(x, y).
        Умеет:
        - сохранять их в файл
        - читать из файла
        - перемещать точку в заданной линии
        - добавлять точку в середину отрезка заданной линии
        - для заданного номера линии и заданной координаты x возвращать координаты точки
    """
    pass

class PhasesModel(Observable):
    """ Содержит данные фазовой картинки
        Умеет:
        - сохранять её в файл
        - читать её из файла
    """
    pass