README (Tracer1.c)

void trace(int* in_array, int height, int width, int int_array_parameter,
	       int period, int true_amount_lines, short* out_array, int* amount_lines) {

	//creates lines
	int* right_array = (int*)malloc(4 * (height + 1) * (width + 1) * sizeof(int));
    int* average_array = (int*)malloc(4 * (height + 1) * sizeof(int));
    double* square_deviations = (double*)malloc(4 * (height + 1) * sizeof(double));
    int* rough_extrems = (int*)malloc(4 * (height + 1) * sizeof(int));
    int* accurate_extrems = (int*)malloc(4 * (height + 1) * sizeof(int));
    int* array_amounts_extrems = (int*)malloc(4 * (width + 1) * sizeof(int));
    int* intermediate_array_extrems = (int*)malloc(4 * (height + 1) * (width + 1) * sizeof(short));

    int rough_amount = 0, accurate_amount = 0, extrem_number = 0, x, y, k = 0, half_period = (int)( period * 0.5);

    //0)the transpose of an array
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            right_array[k] = in_array[j * width + i];
            k++;
        }
    }

    //1)search all extrems
    *amount_lines = height;
    for (int i = 0; i < width; i++) {
        int_array_averaging(int_array_parameter, height, right_array + i * height, average_array);
        //period = search_minimal_period(right_array + i * height, height, very_average_array_parameter);
        create_array_square_deviation(right_array + i * height, height, period, square_deviations);
        rough_search_lows1(square_deviations, height, half_period, rough_extrems, &rough_amount);
        accurate_amount = accurate_search_extremes(rough_extrems, rough_amount, average_array, accurate_extrems);
        for (int j = 0; j < accurate_amount; j++) {
            x = accurate_extrems[j];
            intermediate_array_extrems[extrem_number + j] = x;
        }
        extrem_number = extrem_number + accurate_amount;
        array_amounts_extrems[i] = accurate_amount;
        if (*amount_lines > accurate_amount)
            *amount_lines = accurate_amount;
        if (*amount_lines > true_amount_lines)
            *amount_lines = true_amount_lines;
    }

    //2)creation of out_array
    for (int i = 0; i < *amount_lines; i++) {
        extrem_number = 0;
        for (int j = 0; j < width; j++) {
            x = intermediate_array_extrems[extrem_number + i];
            out_array[i * width + j] = x;
            y = array_amounts_extrems[j];
            extrem_number = extrem_number + y;
        }
    }

    //3)correcting lines
    create_perfect_lines(out_array, *amount_lines, width);

    free(right_array);
    free(average_array);
    free(square_deviations);
    free(rough_extrems);
    free(accurate_extrems);
    free(array_amounts_extrems);
    free(intermediate_array_extrems);
}


1) первая часть - выделение памяти для массивов.
2) транспонирование входного массива. ctypes передает двумерный массив numpy в виде одномерного массива, состоящий из последовательности строчек. Так как программа работает со столбцами массива, его приходится транспонировать.
3.1) int_array_averaging - функция для усреднения значений по нескольким точкам. Функция нужна для избавления от биений.
3.2) search_minimal_period - функция для поиска минимального периода среза. Пока работает плохо, поэтому заменена на хардкод.
3.3) create_array_square_deviation - функция для создания массива, в котором хранятся значения квадратичных отклонений точки входного массива от вершины параболлы. Отклонение считается по некоторому количеству точек (полупериод - пока хардкод). Формула видна из кода. Функция необходима для более точного поиска экстремумов.
3.4) rough_search_lows1 - функция для первичого поиска экстремумов. Она разбивает длину массива на равные отрезки длинной полупериода и на каждом отрезке ищет минимум функции и его абциссу. Эти абциссы - ординаты точек каждой линии. Так как функция - это грубый поиск экстремумов, результат будет передаваться функции accurate_search_extremes для отсеивания лишних точек.
3.5) accurate_search_extremes - функция для отсеивания лишних точек, которые не являются экстремумами. Так как между двумя максимумами лежит один минимум, а между двумя минимумами лежит один максимум, это правило используется для отсеивания. Функция сравнивает значения усредненного массива в трех точках, и если они подходят по выше указанному правилу, то средняя точка входит в выходной массив.
3.6) создаются два массива - массив экстремумов для всего изображения и массив количеств экстремумов в каждом срезе. Так как в каждом срезе может быть разное количество экстремумов, то за количество линий берется минимальное каличество экстремумов.
4) создается одномерный массив, который содержит в себе координаты всех линий. Координата j точки i линии в выходном массиве - это i * width + j номер элемента массива. По сути, этот шаг - это транспонирование массива экстремумов, так как в нем хранятся экстремумы каждого среза (столбца) 
5) create_perfect_lines - функция делает небольшое выпрямление линий, так как после выше указанных манипуляций остаются неправильные точки, которые сильно отклоняются от линий. Чтобы избавиться от них, функция create_perfect_lines берет каждую точку каждой линии, ищет к ней ближайшую и соединяет их прямой, заменяя значения каждой точки на этом отрезке на ординаты прямой. Это последний шаг, результатом всего tracer является полученный массив.
6) освобождение использованной памяти.




