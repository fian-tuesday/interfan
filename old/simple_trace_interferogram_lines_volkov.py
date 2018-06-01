import math
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

filename = r'int-3_0.tif'
lines_distance = 90
base_points_lines_distance_variation = 15
max_line_interruption_distance = 13

lower_trashhold = 60 # порог, ниже которого локальный экстремум считаем чёрной полосой
upper_trashhold = 180  # порог, выше которого локальный экстремум считаем белой полосой
original_folder = r'original'
result_folder = r'result'


def main():
    black_lines, white_lines = trace_interference_lines_on_image(filename)

    #phases = calculate_phases(filename, black_lines, white_lines)

    #save_tif_image(phases, result_folder + '\\' + filename.replace('.tif', '_phase.tif'), 40)
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

    phase_image = Image.new('RGBA', (width, height))
    phase_image.putdata(image_data)
    phase_image.save(filename)
    phase_image.show()


def trace_interference_lines_on_image(image_filename):
    """
    Осуществляет трассировку интерференционных линий на картинке.
    :param image_filename: имя файла исходной картинки
    :return: Возвращает два списка интерференционных линий: чёрных и белых. Причём чёрных на одну больше.
    """
    input_image = Image.open(original_folder + '\\' + image_filename)
    image_data = list(input_image.getdata())
    print('Opened image', image_filename, 'with size', input_image.size, 'and mode', input_image.mode)
    if input_image.mode == 'RGB':
        brightness = [g for r, g, b in image_data]  # Зелёный в данной картинке всегда средний по яркости - берём именно его
    elif input_image.mode == 'RGBA':
        brightness = [g for r, g, b in image_data]  # Зелёный в данной картинке всегда средний по яркости - берём именно его
    else:
        raise ValueError("Unknown image color mode.")
    data_2d = [brightness[i*input_image.width:(i+1)*input_image.width] for i in range(input_image.height)]

    # формируем первые опорные точки (по правой границе картинки == [-1])
    data_slice = [data_2d[y][-1] for y in range(len(data_2d))]
    black_base_points_y, white_base_points_y = get_base_points(data_slice, 15, lambda z: z < lower_trashhold,
                                                               lambda z: z > upper_trashhold)

    # удаляем верхнюю и нижние белые опорные точки, вне области чёрных линий
    white_base_points_y = [y for y in white_base_points_y if black_base_points_y[0] < y < black_base_points_y[-1]]

    # Изобразим границу, на которой будут взяты первые опорные точки для трассировки, вместе с этими точками
    plot_interferogram_slice([data_2d[y][-1] for y in range(len(data_2d))], black_base_points_y, white_base_points_y)

    # проверяем, что чёрных точек на одну больше, чем белых
    assert len(black_base_points_y) == len(white_base_points_y) + 1, 'Шумовые линии на опорном срезе интерферограммы:' \
                                                                 + str(black_base_points_y) + str(white_base_points_y)
    number_of_white_lines = len(white_base_points_y)
    # проверяем, что в опорных точках минимумы и максимумы идут поочерёдно
    assert all(black_base_points_y[i] < white_base_points_y[i] for i in range(number_of_white_lines)), \
        'чёрные и белые точки идут не поочерёдно на опорной границе изображения'

    # Поиск белых и чёрных линий на всей картинке
    black_start_points = [(input_image.width - 1, y) for y in black_base_points_y]
    white_start_points = [(input_image.width - 1, y) for y in white_base_points_y]

    print('Got black and white start points')

    black_lines = [trace_line(data_2d, point) for point in black_start_points]
    white_lines = [trace_line(data_2d, point) for point in white_start_points]

    print('Traced black lines and white lines')

    for lines, color in (black_lines, (255, 0, 0)), (white_lines, (0, 0, 255)):
        for line in lines:
            for x, y in line:
                image_data[y*input_image.width + x] = color

    output_image = Image.new(input_image.mode, input_image.size)
    output_image.putdata(image_data)
    output_image.save(image_filename.replace('.tif', '_trace_new.tif'))
    output_image.show()

    return black_lines, white_lines


def calculate_phases(image_filename, black_lines, white_lines):
    """
    Осуществляет трассировку интерференционных линий на картинке.
    :param image_filename: имя файла исходной картинки
    :param black_lines: список линий, каждая из которых представляет из себя список y[x] точек интерференционной линии.
    :param white_lines: список линий, каждая из которых представляет из себя список y[x] точек интерференционной линии.
    :return: Возвращает два списка интерференционных линий: чёрных и белых. Причём чёрных на одну больше.
    """
    input_image = Image.open(original_folder + '\\' + image_filename)

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


def trace_line(brightness, start_point):
    """ Осуществляет трассировку линии начиная от крайней точки до другого её края
        :param brightness - двумерный массив data_2d[y][x], содержащий яркости пикселей интерферограммы
        :param start_point - tuple(x, y), координаты стартовой крайней точки, от которой начинаем трассировку
        :returns path - путь, это list[tuple(x, y)] - список координат всех точек, входящих в линию
    """

    def ball_trace_step(x, y, old_x, old_y):
        gradient_trashhold = 3

        dx = x - old_x
        dy = y - old_y
        print('DEBUG: x=', x, ', y=', y, ', dx=', dx, ', dy=', dy)
        x += dx
        y += dy

        if x < 0 or y < 0:
            return x, y

        grad_x = (brightness[y - 1][x + 1] - brightness[y - 1][x - 1] +
                  brightness[y + 1][x + 1] - brightness[y + 1][x - 1] +
                  2**0.5*(brightness[y][x + 1] - brightness[y][x - 1])) / (2 + 2**0.5) / 2
        grad_y = (brightness[y + 1][x - 1] - brightness[y - 1][x - 1] +
                  brightness[y + 1][x + 1] - brightness[y - 1][x + 1] +
                  2**0.5*(brightness[y + 1][x] - brightness[y - 1][x])) / (2 + 2**0.5) / 2
        print("DEBUG: grad=", grad_x, grad_y)

        grad_module = (grad_x**2 + grad_y**2)**0.5
        if grad_module < gradient_trashhold:
            print('DEBUG: gradient is small')
            return x, y
        else:
            ddx = -grad_x / grad_module
            ddy = -grad_y / grad_module
            print('DEBUG: gradient is big', ddx, ddy)
            new_x = x + int(ddx*2**0.5)
            new_y = y + int(ddy*2**0.5)
            return new_x, new_y


    def volkov_trace_step(x, y, old_x, old_y):
        def calculate_direction(dx, dy):
            if dx > 0 and dy == 0:
                direction = 0
            elif dx > 0 and dy > 0:
                direction = 1
            elif dx == 0 and dy > 0:
                direction = 2
            elif dx < 0 and dy > 0:
                direction = 3
            elif dx < 0 and dy == 0:
                direction = 4
            elif dx < 0 and dy < 0:
                direction = 5
            elif dx == 0 and dy < 0:
                direction = 6
            elif dx > 0 and dy < 0:
                direction = 7
            else:
                assert False, "dx = 0 and dy = 0. Bad direction!"
            return direction

        projections = [0, 0, 0, 0, 0, 0, 0, 0]
        for direction in range(8):
            dx = int(step_distance * math.cos(math.pi * direction / 4))
            dy = int(step_distance * math.sin(math.pi * direction / 4))
            dr = (dx**2 + dy**2)**0.5
            # print('DEBUG: calc derivative on dx, dy =', dx, dy)
            if (x + dx < 0 or x + dx >= len(brightness[y]) or
                            y + dy < 0 or y + dy >= len(brightness)):
                derivative = 0  # соответствующая точка находится за пределами картинки => считаем производную нулём
            else:
                derivative = (brightness[y + dy][x + dx] - brightness[y][x]) / dr
            for k in range(8):
                projections[k] += abs(derivative) * math.cos(math.pi / 4 * (k - direction))

        old_direction = calculate_direction(x - old_x, y - old_y)
        max_gradient_direction = 0  # choosing the best direction
        for direction in range(0, 8):
            if (direction - 2) % 8 != old_direction and \
                            projections[direction] > projections[max_gradient_direction]:
                max_gradient_direction = direction
        direction = (max_gradient_direction + 2) % 8
        print('DEBUG: chosen direction =', direction)
        x += int(step_distance * math.cos(math.pi * direction / 4))
        y += int(step_distance * math.sin(math.pi * direction / 4))
        return x, y

    trace_step = volkov_trace_step
    step_distance = 10.0
    line = []
    x, y = start_point
    print('DEBUG tracing new line from: ', x, y)
    line.append((x, y))
    old_x, old_y = x, y
    x, y = trace_step(x, y, old_x-1, old_y)
    print('DEBUG: next point =', x, y)
    border_distance = 0
    max_steps = 10
    while (0 + border_distance <= x < len(brightness[0]) - border_distance and
           0 + border_distance <= y < len(brightness) - border_distance):

        line.append((x, y))
        next_point = trace_step(x, y, old_x, old_y)
        old_x, old_y = x, y
        x, y = next_point
        print('DEBUG: next point =', x, y)
        max_steps -= 1
        if max_steps == 0:
            break

    # line.append((x, y))  # add last - border point
    return line


def plot_interferogram_slice(data_slice, base_points1=None, base_points2=None):
    base_points1 = [] if base_points1 is None else base_points1
    base_points2 = [] if base_points2 is None else base_points2
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
    image_data_copy = [(r, g, b) for r, g, b in image_data]
    width = len(all_black_extremal_points)
    height = len(image_data_copy)//width
    for x in range(width):
        for y in all_black_extremal_points[x]:
            image_data_copy[y*width + x] = (0, 0, 255)
        for y in all_white_extremal_points[x]:
            image_data_copy[y*width + x] = (255, 0, 0)

    image = Image.new('RGBA', (width, height))
    image.putdata(image_data_copy)
    image.save(filename)
    image.show()

if __name__ == '__main__':
    main()
