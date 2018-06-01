import math
import numpy as np
import matplotlib.pyplot as plt
import PIL.Image
import PIL.ImageTk
import tkinter
import itertools
import collections


filename = r'int-3_1.tif'
lines_distance = 70
base_points_lines_distance_variation = 69
max_line_interruption_distance = 25

lower_trashhold = 80 # порог, ниже которого локальный экстремум считаем чёрной полосой
upper_trashhold = 170  # порог, выше которого локальный экстремум считаем белой полосой
original_folder = r'original'
result_folder = r'result'

Point = collections.namedtuple('Point', ['x', 'y'])

def main():
    black_lines, white_lines = trace_interference_lines_on_image(filename)

    #TODO: ПЕРЕДЕЛАТЬ РАБОТУ С ФАЗАМИ
    #phases = calculate_phases(filename, black_lines, white_lines)
    #save_tif_image(phases, result_folder + '\\' + filename.replace('.tif', '_phase.tif'), 80)
    #save_phases(phases, result_folder + '\\' + filename.replace('.tif', '_phase.txt'))
    # phases2 = load_phases(result_folder + '\\')


def save_phases(data, filename):
    print('saving', filename)
    height = len(data)
    width = len(data[0])
    with open(filename, 'w') as f:
        for y in range(height):
            for x in range(width):
                val = data[y][x]
                f.write(str(val) + '\t')
            f.write('\n')


def load_phases(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            data.append(row)
    return data


def save_tif_image(data, filename, scale=255):
    print('saving', filename)
    height = len(data)
    width = len(data[0])
    image_data = [(0, 0, 0)] * (height*width)
    for y in range(height):
        for x in range(width):
            val = data[y][x]
            if val > scale:
                color = (0, 255, 0)
            elif val < -scale:
                color = (0, 0, 255)
            elif val >= 0:
                color = (round(val/scale * 255),)*3
            else:
                color = (round(-val/scale *255), 0, 0)
            image_data[y * width + x] = color

    phase_image = PIL.Image.new('RGBA', (width, height))
    phase_image.putdata(image_data)
    phase_image.save(filename)
    phase_image.show()

"""
def interactive_trace_line(filename_extremal):
    def mouse_callback(event):
        nonlocal old_click, pictured_line
        print("clicked at", event.x, event.y)
        if old_click is not None:
            canvas.create_line(old_click[0], old_click[1], event.x, event.y, fill='lightgreen')
        old_click = event.x, event.y
        pictured_line.append(old_click)

    pil_image = PIL.Image.open(filename_extremal)
    width, height = pil_image.width, pil_image.height
    root = tkinter.Tk()
    image = PIL.ImageTk.PhotoImage(pil_image)
    sizes = "{0}x{1}".format(width, height)
    print(sizes)
    root.geometry(sizes)
    canvas = tkinter.Canvas(root, width=width, height=height)
    canvas.pack()
    image_sprite = canvas.create_image(width//2, height//2, image=image)

    pictured_line = []
    old_click = None
    canvas.bind('<Button-1>', mouse_callback)
    canvas.bind('<Button-3>', lambda event: root.destroy())
    root.mainloop()

    return pictured_line
"""


class TraceLine:
    def __init__(self, tk_canvas, list_of_points: list, color):
        self._list_of_points = list_of_points  # Важно сохранение ссылки на тот же список!
        self._canvas = tk_canvas
        self._points_avatars = [None]*len(list_of_points)
        #self._segment_avatars = [None]*(len(list_of_points) - 1)
        self._avatars_point_index = {}

        # создаём изображения (аватары) точек
        for index in range(len(list_of_points)):
            x, y = list_of_points[index]
            avatar = tk_canvas.create_oval(x-1, y-1, x+1, y+1, fill=color, activefill='orange')
            self._avatars_point_index[avatar] = index
            self._points_avatars[index] = avatar
        # создаём изображения (аватары) отрезков
        #for index in range(len(list_of_points)-1):
        #    (x1, y1), (x2, y2) = list_of_points[index], list_of_points[index+1]
        #    avatar = tk_canvas.create_line(x1, y1, x2, y2, fill=color)
        #    self._segment_avatars[index] = avatar

    def _move_point(self, point_avatar, x, y):
        assert point_avatar in self._points_avatars

        index = self._avatars_point_index[point_avatar]
        self._list_of_points[index] = (x, y)  # Это главное, а далее только отображаем изменения аватаров
        self._canvas.coords(point_avatar, x-1, y-1, x+1, y+1)
        if index > 0:  # Если это не самая левая точка, то у неё есть сегмент (отезок) линии слева
            pass  # TODO
        if index < len(self._list_of_points) - 1:  # Если это не самая правая точка, то у неё есть сегмент линии справа
            pass  # TODO


class ClickEventsDispatcher:
    def __init__(self, canvas):
        """
        Диспетчеризует события от мышки по интерференционным линиям

        :param canvas: Tkinter canvas
        :param trace_lines:
        """
        self._canvas = canvas
        self._mouse_is_holding_a_point = False
        self._trace_line_object_by_avatar = {}

        canvas.bind('<ButtonPress-1>', lambda event: self.mouse_pick_point_callback(event))
        canvas.bind('<ButtonRelease-1>', lambda event: self.mouse_drop_point_callback(event))
        canvas.bind('<B1-Motion>', lambda event: self.mouse_move_point_callback(event))

    def register_trace_line_object(self, trace_line: TraceLine):
        for avatar in trace_line._points_avatars:
            self._trace_line_object_by_avatar[avatar] = trace_line

    def mouse_pick_point_callback(self, event):
        search_result = self._canvas.find_closest(event.x, event.y)  # TODO: искать только среди точек
        if len(search_result) != 1:
            print('Found several avatars instead of one:', search_result)
            return
        avatar = search_result[0]
        if avatar not in self._trace_line_object_by_avatar:
            print('Found strange avatar, which is not registered as a point of line:', avatar)
            return
        self._mouse_is_holding_a_point = True
        self._holding_point_avatar = avatar
        clicked_trace_line = self._trace_line_object_by_avatar[avatar]
        clicked_trace_line._move_point(avatar, event.x, event.y)

    def mouse_move_point_callback(self, event):
        if self._mouse_is_holding_a_point:
            avatar = self._holding_point_avatar
            clicked_trace_line = self._trace_line_object_by_avatar[avatar]
            clicked_trace_line._move_point(avatar, event.x, event.y)

    def mouse_drop_point_callback(self, event):
        self._mouse_is_holding_a_point = False
        self._holding_point_avatar = None


def interactively_fix_traced_lines(image_filename, black_lines, white_lines):
    print("Доехали!")
    pil_image = PIL.Image.open(image_filename)
    width, height = pil_image.width, pil_image.height
    root = tkinter.Tk()
    image = PIL.ImageTk.PhotoImage(pil_image)
    sizes = "{0}x{1}".format(width, height)
    root.geometry(sizes)
    canvas = tkinter.Canvas(root, width=width, height=height)
    canvas.pack()
    image_sprite = canvas.create_image(width//2, height//2, image=image)

    canvas.bind('<Button-3>', lambda event: root.destroy())
    dispatcher = ClickEventsDispatcher(canvas)

    for lines, color in (black_lines, 'red'), (white_lines, 'blue'):
        for line in lines:
            trace_line = TraceLine(canvas, line, color)
            print('line registered')
            dispatcher.register_trace_line_object(trace_line)

    # В этот момент можно подправить линии интерактивно в Tkinter
    root.mainloop()


def trace_interference_lines_on_image(image_filename):
    """
    Осуществляет трассировку интерференционных линий на картинке.
    :param image_filename: имя файла исходной картинки
    :return: Возвращает два списка интерференционных линий: чёрных и белых. Причём чёрных на одну больше.
    """

    input_image = PIL.Image.open(original_folder + '\\' + image_filename)
    image_data = list(input_image.getdata())
    print('Opened image', image_filename, 'with size', input_image.size, 'and mode', input_image.mode)
    if input_image.mode == 'RGB':
        brightness = [g for r, g, b in image_data]  # Зелёный в данной картинке всегда средний по яркости - берём именно его
    elif input_image.mode == 'RGBA':
        brightness = [g for r, g, b,a in image_data]  # Зелёный в данной картинке всегда средний по яркости - берём именно его
    else:
        raise ValueError("Unknown image color mode.")
    data_2d = [brightness[i*input_image.width:(i+1)*input_image.width] for i in range(input_image.height)]

    # формируем первые опорные точки (по правой границе картинки == [-1])
    data_slice = [data_2d[y][-1] for y in range(len(data_2d))]
    black_base_points, white_base_points = get_base_points(data_slice, 15, lambda z: z < lower_trashhold,
                                                           lambda z: z > upper_trashhold)

    # удаляем верхнюю и нижние белые опорные точки, вне области чёрных линий
    white_base_points = [y for y in white_base_points if black_base_points[0] < y < black_base_points[-1]]

    # Изобразим границу, на которой будут взяты первые опорные точки для трассировки, вместе с этими точками
    #plot_interferogram_slice([data_2d[y][-1] for y in range(len(data_2d))], black_base_points, white_base_points)

    # проверяем, что чёрных точек на одну больше, чем белых
    assert len(black_base_points) == len(white_base_points) + 1, 'Шумовые линии на опорном срезе интерферограммы:' \
                                                                 + str(black_base_points) + str(white_base_points)
    number_of_white_lines = len(white_base_points)
    # проверяем, что в опорных точках минимумы и максимумы идут поочерёдно
    assert all(black_base_points[i] < white_base_points[i] for i in range(number_of_white_lines)), \
        'чёрные и белые точки идут не поочерёдно на опорной границе изображения'
    # Поиск белых и чёрных линий на всей картинке
    all_black_extremal_points = []
    all_white_extremal_points = []
    for x in range(input_image.width):
        data_slice = [data_2d[y][x] for y in range(len(data_2d))]
        black_extremal_points = get_extremal_points(data_slice, 31, True,  lambda z: z < lower_trashhold)
        white_extremal_points = get_extremal_points(data_slice, 51, False, lambda z: z > upper_trashhold)
        all_black_extremal_points.append(black_extremal_points)
        all_white_extremal_points.append(white_extremal_points)

    filename_extremal = result_folder + '\\' + filename.replace('.tif', '_extremal.tif')
    save_extremal_points_image(filename_extremal, image_data, all_black_extremal_points, all_white_extremal_points)

    """ Трассировка линий НОВАЯ ВЕРСИЯ!!!"""
    # black_lines и white_lines - это списки точек, т.е. кортежей двух координат (x, y)
    black_lines = []
    white_lines = []
    # линии перебираем по очереди: чёрные, затем белые
    for i in range(number_of_white_lines + 1):
        right_point = Point(input_image.width - 1, black_base_points[i])
        line = trace_line(right_point, all_black_extremal_points)
        black_lines.append(line)
        
    for i in range(number_of_white_lines):
        right_point = Point(input_image.width - 1, white_base_points[i])
        line = trace_line(right_point, all_white_extremal_points)
        # TODO:  раньше была возможность проверки, не вылазим ли белой за соседние чёрные - теперь она поломана
        # redunant:, black_lines[i], black_lines[i + 1])
        white_lines.append(line)

    interactively_fix_traced_lines(filename_extremal, black_lines, white_lines)

    return black_lines, white_lines


def calculate_phases(image_filename, black_lines, white_lines):
    """
    Осуществляет трассировку интерференционных линий на картинке.
    :param image_filename: имя файла исходной картинки
    :param black_lines: список линий, каждая из которых представляет из себя список y[x] точек интерференционной линии.
    :param white_lines: список линий, каждая из которых представляет из себя список y[x] точек интерференционной линии.
    :return: Возвращает два списка интерференционных линий: чёрных и белых. Причём чёрных на одну больше.
    """
    input_image = PIL.Image.open(original_folder + '\\' + image_filename)

    # сообщаем каждой точке ее фазу
    phase = [[0] * input_image.width for i in range(input_image.height)]
    for j in range(input_image.width):
        numberline = 0
        for i in range(input_image.height):
            if (i == black_lines[numberline // 2][j]) or (
                    i <= white_lines[-1][j] and i == white_lines[numberline // 2][j]):
                phase[i][j] = (numberline + 1) * math.pi  # в точках максимума-минимума pi*n
                numberline += 1
            elif i < black_lines[0][j]:
                #phase[i][j] = math.pi * (0.5 + 0.5 * math.sin(-math.pi / 2 + math.pi * i / black_lines[0][j]))
                phase[i][j] = math.pi * (i / black_lines[0][j])
            elif numberline == len(black_lines) + len(white_lines):  # после последней чёрной линии
                #phase[i][j] = math.pi * (
                #numberline + 0.5 + 0.5 * math.sin(-math.pi / 2 + math.pi * (i - black_lines[numberline // 2][j]) /
                #                                  (input_image.height - black_lines[numberline // 2][j])))
                phase[i][j] =math.pi * (numberline + (i - black_lines[numberline // 2][j]) /(input_image.height - black_lines[numberline // 2][j]))
            elif (numberline % 2 == 1):  # между ними интерполируем по синусоиде
                # DEBUG
                # print(i, j, white_lines[numberline//2][j], black_lines[numberline//2][j])
                #phase[i][j] = numberline * math.pi + math.pi * (
                #0.5 + 0.5 * math.sin(-math.pi / 2 + math.pi * (i - black_lines[numberline // 2][j])
                #                     / (white_lines[numberline // 2][j] - black_lines[numberline // 2][j])))
                print(i,j,numberline,white_lines[numberline // 2][j],black_lines[numberline // 2][j])
                phase[i][j] = numberline * math.pi + math.pi * ((i - black_lines[numberline // 2][j]) / (white_lines[numberline // 2][j] - black_lines[numberline // 2][j]))
            elif (numberline % 2 == 0):
               # phase[i][j] = numberline * math.pi + math.pi * \
                #              (0.5 + 0.5 * math.sin(-math.pi / 2 + math.pi * (i - white_lines[numberline // 2 - 1][j])/
                #                     (black_lines[numberline // 2][j] - white_lines[numberline // 2 - 1][j])))
                phase[i][j] = numberline * math.pi + math.pi *(i - white_lines[numberline // 2 - 1][j])/ (black_lines[numberline // 2][j] -white_lines[numberline // 2 - 1][j])
            else:
                raise Exception()

    return phase


def get_base_points(data, number_of_approximation_points, black_trash_filter=None, white_trash_filter=None):
    # приближаем значения в соседних N точках наилучшими параболами
    # и считаем хи квадрат отлонений
    # search_min - булево значение, True - ищем минимум, значит интересны только положительные a
    # black_trash_filter, white_trash_filter - функция для фильтрации значений минимумов/максимумов
    N = number_of_approximation_points // 2
    khi2_for_y = [None] * N
    for y in range(N, len(data) - N):
        A = 2 * sum(i ** 4 for i in range(1, N + 1))
        B = 2 * sum((data[y] - data[y + i]) * (i ** 2) for i in range(-N, N + 1))
        C = sum((data[y + i] - data[y]) ** 2 for i in range(-N, N + 1))
        a_optimal = -B / (2 * A)
        khi2 = A * a_optimal ** 2 + B * a_optimal + C
        # print(y, data[y], khi2, A, B, C, a_optimal, sep='\t')  # DEBUG
        khi2_for_y.append(khi2)

    # ищем первую базовую линию
    y0 = N + 2
    while y0 < len(data) - N - 3:
        y = y0
        if (khi2_for_y[y] <= khi2_for_y[y - 1] and
                    khi2_for_y[y] <= khi2_for_y[y + 1] and
                    khi2_for_y[y] <= khi2_for_y[y - 2] and
                    khi2_for_y[y] <= khi2_for_y[y + 2]):
            if not black_trash_filter or black_trash_filter(data[y]):
                A = 2 * sum(i ** 4 for i in range(1, N + 1))
                B = 2 * sum((data[y] - data[y + i]) * (i ** 2) for i in range(-N, N + 1))
                a_optimal = -B / (2 * A)
                if a_optimal > 0:
                    break
        y0 += 1

    black_base_points = []
    white_base_points = []
    search_min = True
    trash_filter = black_trash_filter
    while y0 < len(data) - N - 3:
        for y in (y0 + (1 - 2 * (i % 2)) * (i + 1) // 2 for i in
                  range(2 * base_points_lines_distance_variation + 1)):  # 0, -1, 1, -2, 2, -3, 3, -4, 4, -5
            if (y >= len(data) - N - 3
                or 285 <= y <= 315):  # FIXME: hardcoded BUG to escape bad min/max area in origin.tif!!!
                continue
            if (khi2_for_y[y] <= khi2_for_y[y - 1] and
                        khi2_for_y[y] <= khi2_for_y[y + 1] and
                        khi2_for_y[y] <= khi2_for_y[y - 2] and
                        khi2_for_y[y] <= khi2_for_y[y + 2]):
                if not trash_filter or trash_filter(data[y]):
                    A = 2 * sum(i ** 4 for i in range(1, N + 1))
                    B = 2 * sum((data[y] - data[y + i]) * (i ** 2) for i in range(-N, N + 1))
                    a_optimal = -B / (2 * A)
                    if search_min == (a_optimal > 0):
                        y0 = y
                        break
        else:
            print("ERROR: can't find khi^2 minimum around y0=" + str(y0) + " +- " + str(
                base_points_lines_distance_variation))
            # raise Exception()

        if search_min:
            black_base_points.append(y0)
            print(y0, ' black')
            trash_filter = white_trash_filter
        elif not search_min:
            white_base_points.append(y0)
            print(y0, ' white')
            trash_filter = black_trash_filter
        search_min = not search_min

        y0 += lines_distance // 2

    return black_base_points, white_base_points


def get_extremal_points(data, number_of_approximation_points, search_min, trash_filter=None):
    # приближаем значения в соседних N точках наилучшими параболами
    # и считаем хи квадрат отлонений
    # search_min - булево значение, True - ищем минимум, значит интересны только положительные a
    # trash_filter - функция для фильтрации значений минимумов/максимумов
    N = number_of_approximation_points//2
    khi2_for_y = [None]*N
    for y in range(N, len(data)-N):
        A = 2*sum(i**4 for i in range(1, N+1))
        B = 2*sum((data[y]-data[y+i])*(i**2) for i in range(-N, N+1))
        C = sum((data[y+i]-data[y])**2 for i in range(-N, N+1))
        a_optimal = -B/(2*A)
        khi2 = A*a_optimal**2 + B*a_optimal + C
        # print(y, data[y], khi2, A, B, C, a_optimal, sep='\t')  # DEBUG
        khi2_for_y.append(khi2)

    y = N+2
    extremal_points = []
    while y < len(data)-N-3:
        if (khi2_for_y[y] <= khi2_for_y[y-1] and
                khi2_for_y[y] <= khi2_for_y[y+1] and
                khi2_for_y[y] <= khi2_for_y[y-2] and
                khi2_for_y[y] <= khi2_for_y[y+2]):
            if not trash_filter or trash_filter(data[y]):
                A = 2 * sum(i ** 4 for i in range(1, N + 1))
                B = 2 * sum((data[y] - data[y + i]) * (i ** 2) for i in range(-N, N + 1))
                a_optimal = -B/(2*A)
                if search_min and a_optimal > 0 or not search_min and a_optimal < 0:
                    extremal_points.append(y)
        y += 1
    return extremal_points


def trace_line(start_point, extremal_points, lower_border_line = None, upper_border_line = None):
    """ Осуществляет трассировку линии справа-налево, шагая по базовым точкам.
        :param start_point: опорная точка, от которой начинается трассировка
        :param extremal_points: список или множество координат y точек, похожих на точки линий данного типа
        :param lower_border_line: пограничная линия с меньшими y (на рисунке сверху), за которые нельзя вылезать
        :param upper_border_line: пограничные линии с большими y (на рисунке снизу), за которые нельзя вылезать

        :return: список координат (x, y) точек трассируемой линии
    """
    line = []
    old_x, old_y = start_point
    for x in range(old_x - 1, -1, -1):
        for dy in ((1-2*(i%2))*(i+1)//2 for i in range(max_line_interruption_distance*2+1)):  # 0, +1, -1, +2, -2, +3, -3, +4, -4, +5, -5, +6, -6, +7, -7
            y = old_y + dy
            # проверяем выход за пограничные линии
            # TODO: ПРОВЕРКА ПОКА ОТКЛЮЧЕНА В СВЯЗИ С ТЕМ, ЧТО ЭТИ ЛИНИИ ПОМЕНЯЛИ ТИП!!!
            #if lower_border_line and y <= lower_border_line[x] or upper_border_line and y >= upper_border_line[x]:
            #    continue  # пропускаем такую точку
            if y in extremal_points[x]:
                # найдена точка данной линии в координатах (x, y)
                line.append(Point(x, y))
                old_x, old_y = x, y
                break
    return line


def plot_interferogram_slice(data_slice, base_points1=[], base_points2=[]):
    # равномерно распределённые значения от 0 до len(data), с шагом 1
    t = np.arange(0., len(data_slice), 1.)
    dat = np.array(data_slice)
    plt.plot(t, dat, 'b')

    if base_points1:
        base_points_values = [data_slice[x] for x in base_points1]
        plt.plot(base_points1, base_points_values, 'r*')
    if base_points2:
        base_points_values = [data_slice[x] for x in base_points2]
        plt.plot(base_points2, base_points_values, 'g*')
    
    plt.show()


def save_extremal_points_image(filename, image_data, all_black_extremal_points, all_white_extremal_points):
    print('saving extremal points in file:', filename)
    image_data_copy = [(r, g, b) for r, g, b,a in image_data]
    width = len(all_black_extremal_points)
    height = len(image_data_copy)//width
    for x in range(width):
        for y in all_black_extremal_points[x]:
            image_data_copy[y*width + x] = (0, 0, 255)
        for y in all_white_extremal_points[x]:
            image_data_copy[y*width + x] = (255, 0, 0)

    image = PIL.Image.new('RGBA', (width, height))
    image.putdata(image_data_copy)
    image.save(filename)
    #image.show()

if __name__ == '__main__':
    main()
