#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <math.h>

void test_load(int* array, int height, int width) {
    FILE* f = fopen("/home/vladimir/projects_py/test_load.txt", "w");
    int* right_array = (int*)malloc(4 * (height + 1) * (width + 1) * sizeof(int));
    int k = 0;
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            right_array[k] = array[j * width + i];
            k++;
        }
    }
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            fprintf(f, "%d\n", right_array[i * height + j]);
        }
        fprintf(f, "***********************************************************************\n");
    }
    fclose(f);
}

int int_max(int* int_array, int length) {

	//finding the maximum value for an int array

	int res = 0;
	for (int i = 0; i < length; i++) {
		if (res < int_array[i])
			res = int_array[i];
	}

	return res;
}

void double_max(double* double_array, int length, double* result) {

	//finding the maximum value for an double array

	*result = 0.0;

	for (int i = 0; i < length; i++) {
		if (*result < double_array[i])
			*result = double_array[i];
	}

}

int int_min(int* int_array, int length) {

	//finding the minimum value for an int array

	int result = int_max(int_array, length);
	for (int i = 0; i < length; i++) {
		if (result > int_array[i])
			result = int_array[i];
	}

	return result;
}

void double_min(double* double_array, int length, int* k_min, double* result) {

	//finding the minimum value for an double array

	double_max(double_array, length, result);
	for (int i = 0; i < length; i++) {
		if (*result > double_array[i]) {
			*result = double_array[i];
			if (k_min != NULL)
				*k_min = i;
		}
	}
}

void calculation_interval(int x, int length, int parameter, int* start, int* finish) {

	//calculating the start and end of an interval of
	//length <= 2 * parameter to which the point x belongs
	int amount_points = parameter;  //number of points for aveaging


	if (x < amount_points) {
		*start = 0;
		*finish = x + amount_points;
	}
	else if (x >= length - amount_points) {
		*start = x - amount_points;
		*finish = length;
	}
	else {
		*start = x - amount_points;
		*finish = x + amount_points;
	}
}

void int_array_averaging(int int_array_parameter, int length, int* in_array, int* out_array) {

	//averaging an array over several points, the number of which is equal to parameter

	int sum, start = 0, finish = 0;     //start and finish belongs interval

	for (int i = 0; i < length; i++) {
		calculation_interval(i, length, int_array_parameter, &start, &finish);
		sum = 0;
		for (int j = start; j < finish; j++) {
			sum = sum + in_array[j];
		}
		out_array[i] = (int)(sum / (finish - start));
	}
}

int search_amount_intersections(int* array, int length, int y) {
    int result = 0;

    for (int i = 0; i < length - 1; i++) {
        if (((array[i] < y) &&  (y <= array[i + 1])) ||
            ((array[i] > y) &&  (y >= array[i + 1]))) {
                result++;
            }
    }
    return result;
}

int search_minimal_period(int* array, int length) {
    int max = int_max(array, length);
    int min = int_min(array, length);
    int frequency = 0, true_amount = 0, intermediate_amount, true_y, x1, x2, result = length, inter_frequency;
    int number_intersection = 0, period = length, amount_lines = 0, number_period = 0, test;

    // 0) search for the most frequent quantity
    int* array_amounts = (int*)malloc(4 * (max - min + 1) * sizeof(int));
    for (int y = min; y <= max; y++) {
        array_amounts[y - min] = search_amount_intersections(array, length, y);
        test = array_amounts[y - min];
    }
    for (int i = 0; i <= max - min; i++) {
        intermediate_amount = array_amounts[i];
        inter_frequency = 0;
        for (int j = 0; j <= max - min; j++) {
            if (intermediate_amount == array_amounts[j])
                inter_frequency++;
        }
        if (inter_frequency > frequency) {
            frequency = inter_frequency;
            true_amount = intermediate_amount;
        }
    }

    // 1) creation of the array of intersections
    int* array_intersections = (int*)malloc(4 * (true_amount + 1) * (max - min + 1) * sizeof(int));
    for (int y = min; y <= max; y++) {
        intermediate_amount = array_amounts[y - min];
        if (true_amount == intermediate_amount) {
            for (int i = 0; i < length - 1; i++) {
                if (((array[i] < y) &&  (y <= array[i + 1])) ||
                    ((array[i] > y) &&  (y >= array[i + 1]))) {
                        array_intersections[number_intersection] = i;
                        test = array_intersections[number_intersection];
                        number_intersection++;
                    }
            }
            amount_lines++;
        }
    }

    // 2) create array of average periods
    int* periods = (int*)malloc(4 * (true_amount + 1) * sizeof(int));
    for (int i = 0; i < true_amount - 2; i++) {
        periods[number_period] = 0;
        test = periods[number_period];
        for (int j = 0; j < amount_lines; j++) {
            x1 = j * true_amount + i + 2;
            x2 = j * true_amount + i;
            test = array_intersections[x1] - array_intersections[x2];
            periods[number_period] = periods[number_period] + array_intersections[x1] - array_intersections[x2];
            test = periods[number_period];
        }
        periods[number_period] = periods[number_period] / amount_lines;
        number_period++;
    }

    for (int i = 0; i < true_amount - 2; i++) {
        if (result > periods[i])
            result = periods[i];
    }
    free(array_amounts);
    free(periods);
    free(array_intersections);
    return result;
}

void double_array_averaging(int double_array_parameter, int length, double* in_array, double* out_array) {

	//averaging an array over several points, the number of which is equal to parameter
	//if flag = 0, array will has only int values
	//if flag = 1, array will has only double values

	int start = 0, finish = 0;     //start and finish belongs interval
	double sum;

	for (int i = 0; i < length; i++) {
		calculation_interval(i, length, double_array_parameter, &start, &finish);
		sum = 0;
		for (int j = start; j < finish; j++) {
			sum = sum + in_array[j];
		}
		out_array[i] = sum / (finish - start);
	}
}

void create_array_square_deviation(int* array, int length, int period, double* result_array) {

	//calculation of the square deviation of each
	//point of the array from the vertex of the parabola

	long sum1, sum2, sum3;      //variables for calculating the square deviation
	double res;
	int start = 0, finish = 0;
	period = (int)(period / 2);

	for (int i = 0; i < length; i++) {
		calculation_interval(i, length, period, &start, &finish);
		sum1 = 0;
		sum2 = 0;
		sum3 = 0;
		for (int j = start; j < finish; j++) {
			sum1 = sum1 + pow((array[j] - array[i]), 2);
			sum2 = sum2 + (array[j] - array[i]) * pow((j - i), 2);
			sum3 = sum3 + pow((j - i), 4);
		}
		res = sum1 - 3 * (pow(sum2, 2)) / (4 * sum3);
		result_array[i] = res;
	}
}

void rough_search_lows3(double* array, int length, int period, int* result_array, int* amount_rough_lows) {
    double min = 0;
    int i = 0, k_min = 0, x = 0, number = 0;

    double_min(array, period, &x, &min);
    while (i < length) {
        double_min(array + i, period, &k_min, &min);
        if ((i < length) && (x == k_min)) {
            while ((i < length) && (x == k_min)) {
                double_min(array + i, period, &k_min, &min);
                i++;
            }
            result_array[number] = x;
            number++;
        }
        x = k_min;
        i++;
    }
    *amount_rough_lows = number;
}

void rough_search_lows2(double* array, int length, int double_array_parameter, int* result_array, int* amount_minima) {

	//create an array of minims on each segment
	//with a length equal to the minimum period
	int amount_intersections = 0, flag = 0, x = 0;  //k_min - x of min
													//if function decreases, flag = 0
													//if function increases, flag = 1
	double max = 0.0, min = 0.0;
	double_max(array, length, &max);
    double_min(array, length, &x, &min);
	double middle = (max + min) / 2;
	int* array_intersections = (int*)malloc(4 * (length + 1) * sizeof(int));
	double* average_array = (double*)malloc(4 * (length + 1) * sizeof(double));

	double_array_averaging(double_array_parameter, length, array, average_array);
	//1) divide the length into segments at the intersections
	for (int i = 0; i < length - 1; i++) {
		//for the first intersection of the function, only this case is important
		if ((amount_intersections == 0) && (array[i] <= middle) && (middle < array[i + 1])) {
			array_intersections[0] = 0;
			array_intersections[1] = i;
			amount_intersections = 2;
			flag = 0;
		}
		else if (((array[i] >= middle) && (middle > array[i + 1]) && (flag == 0)) ||   //function is decreasing and flag = 0
			((array[i] <= middle) && (middle < array[i + 1]) && (flag == 1))) {        //function is increasing and flag = 1
			array_intersections[amount_intersections] = i;
			amount_intersections++;
			flag = (flag + 1) % 2;		//changing the sign of the derivative
		}
	}
	//for the last intersection of the function, only this case is important
	if (flag == 1) {
		array_intersections[amount_intersections] = length - 1;
		amount_intersections++;
	}

	//2)search for the minimum value on individual segments
	double minimum_separate_segment = 0;
	int k_min = 0;      //k_min is x of minimum_value_separate_segment

	for (int i = 0; i < amount_intersections; i = i + 2) {
		double_min(&(array[array_intersections[i]]), array_intersections[i + 1] - array_intersections[i], &k_min, &minimum_separate_segment);
		result_array[i / 2] = array_intersections[i] + k_min;
	}
	*amount_minima = amount_intersections / 2;
	free(array_intersections);
	free(average_array);
}

void rough_search_lows1(double* array, int length, int period, int* rough_lows, int* amount_rough_lows) {
    int k_min = 0, number;
    double min = 0;

    if ((length % period) != 0) {
        number = (int)((length / period) + 1);
    }
    else {
        number = (int)(length / period);
    }
    *amount_rough_lows = number;

    for (int i = 0; i < *amount_rough_lows; i++) {
        double_min(&(array[i * period]), period, &k_min, &min);
        rough_lows[i] = i * period + k_min;
    }

}

int accurate_search_extremes(int* x_array, int length, int* y_array, int* result_array) {

	//specification of extremum coordinates

	int j = 1, extrem_number = 1;      //it is amount of extrems
	int x1, x, x2, y1, y, y2;

	result_array[0] = x_array[0];
	while (j < length - 1) {
	    x1 = result_array[extrem_number - 1];
	    x = x_array[j];
	    x2 = x_array[j + 1];
	    y1 = y_array[x1];
	    y = y_array[x];
	    y2 = y_array[x2];
	    if (((y1 < y) && (y2 < y)) ||
	        ((y1 > y) && (y2 > y))) {
	            result_array[extrem_number] = x;
	            extrem_number++;
	        }
	    j++;
	}
	result_array[extrem_number] = x_array[length - 1];
	extrem_number++;
	return extrem_number;
}

int search_nearest_point(short* line, int width, int x) {
    int result_point, min = width * width, k_min, r;

    for (int i = x + 1; i < width; i++) {
        r = (i - x) * (i - x) + (line[i] - line[x]) * (line[i] - line[x]);
        if (min > r) {
            k_min = i;
            min = r;
        }
    }
    return k_min;
}

void create_perfect_lines(short* lines, int amount_lines, int width) {
    int start, end, y1, y2, x1, x2;
    double k, b;
    short y;
    short* one_line = lines;

    for (int i = 0; i < amount_lines; i++) {
        start = 0;
        end = 1;
        one_line = &(lines[i * width]);
        while(end < width) {
            end = search_nearest_point(one_line, width, start);
            x1 = start;
            x2 = end;
            y1 = one_line[x1];
            y2 = one_line[x2];
            k = (y2 - y1) / (x2 - x1);
            for (int j = start; j < end; j++) {
                y = (short)(y1 + k * (j - x1));
                one_line[j] = y;
            }
            start = end;
            end++;
        }
    }
}

void trace(int* in_array, int height, int width, int int_array_parameter,
	       int true_amount_lines, short* out_array, int* amount_lines) {

	//creates lines
	int* right_array = (int*)malloc(4 * (height + 1) * (width + 1) * sizeof(int));
    int* average_array = (int*)malloc(4 * (height + 1) * sizeof(int));
    double* square_deviations = (double*)malloc(4 * (height + 1) * sizeof(double));
    int* rough_extrems = (int*)malloc(4 * (height + 1) * sizeof(int));
    int* accurate_extrems = (int*)malloc(4 * (height + 1) * sizeof(int));
    int* array_amounts_extrems = (int*)malloc(4 * (width + 1) * sizeof(int));
    int* intermediate_array_extrems = (int*)malloc(4 * (height + 1) * (width + 1) * sizeof(short));

    int rough_amount = 0, accurate_amount = 0, extrem_number = 0, x, y, k = 0, half_period, quarter_period;

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
        half_period = search_minimal_period(average_array, height);
        half_period = (int)half_period / 2;
        quarter_period = half_period / 2;
        create_array_square_deviation(right_array + i * height, height, half_period, square_deviations);
        rough_search_lows1(square_deviations, height, quarter_period, rough_extrems, &rough_amount);
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


