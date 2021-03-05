#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <math.h>

void create_base_points_x(int width, int amount_lines, int amount_points, short* base_points_x) {
    int amount_segments = amount_points - 1;
    for (int i = 0; i < amount_lines; i++) {
    base_points_x[i * amount_points] = 0;
        for (int j = 1; j < amount_points - 1; j++) {
            base_points_x[i * amount_points + j] = base_points_x[i * amount_points + j - 1] + width / amount_segments;
        }
    base_points_x[i * amount_points + amount_points - 1] = width - 1;
    }
}

void test_base_points_x(int width, int amount_lines, int amount_points) {
    FILE* f = fopen("test_base_points_x.txt", "w");
    short* base_points_x = (short*)malloc(4 * (amount_lines + 1) * (amount_points + 1) * sizeof(short));

    create_base_points_x(width, amount_lines, amount_points, base_points_x);
    for (int i = 0; i < amount_lines; i++) {
        for (int j = 0; j < amount_points; j++) {
            fprintf(f, "%d - %hi\n", i * amount_points + j, base_points_x[i * amount_points + j]);
        }
        fprintf(f, "*****************************************\n");
    }
    fclose(f);
    free(base_points_x);
}

void create_base_points_y(short* array, short* base_points_x, int width, int amount_lines, int amount_points, short* base_points_y) {
    short test;

    for (int i = 0; i < amount_lines; i++) {
        for (int j = 0; j < amount_points; j++) {
            base_points_y[i * amount_points + j] = array[i * width + base_points_x[i * amount_points + j]];
        }
    }
}

void test_base_points_y(short* array, short* base_points_x, int width, int amount_lines, int amount_points) {
    FILE* f = fopen("base_points_y.txt", "w");
    short* base_points_y = (short*)malloc(4 * (amount_lines + 1) * (amount_points + 1) * sizeof(short));

    create_base_points_y(array, base_points_x, width, amount_lines, amount_points, base_points_y);
    for (int i = 0; i < amount_lines; i++) {
        for (int j = 0; j < amount_points; j++) {
            fprintf(f, "%d %hi - %hi\n", i * amount_points + j, base_points_x[i * amount_points + j], base_points_y[i * amount_points + j]);
        }
        fprintf(f, "*******************************************************************\n");
    }
    fclose(f);
    free(base_points_y);
}

void calculation_coefficients_cubic_spline (short* y_array, short* x_array, int amount_points,
                                            double* a, double* b, double* c) {
    double* alfa = (double*)malloc(4 * amount_points * sizeof(double));
    double* beta = (double*)malloc(4 * amount_points * sizeof(double));
    double* x = (double*)malloc(4 * amount_points * sizeof(double));
    double* y = (double*)malloc(4 * amount_points * sizeof(double));
    double* z = (double*)malloc(4 * amount_points * sizeof(double));
    double* s = (double*)malloc(4 * amount_points * sizeof(double));
    int n = amount_points - 2;
    double test;
    int test1;
    // 0) creation of matrix (xyz) * b = s
    for (int i = 1; i <= n; i++) {
        x[i] = x_array[i] - x_array[i - 1];
        test1 = x[i];
        y[i] = 2 * (x_array[i + 1] - x_array[i - 1]);
        test1 = y[i];
        z[i] = x_array[i + 1] - x_array[i];
        test1 = z[i];
        s[i] = 3 * ((y_array[i + 1] - y_array[i]) /(double)(x_array[i + 1] - x_array[i]) -
               (y_array[i] - y_array[i - 1]) /(double)(x_array[i] - x_array[i - 1]));
        test = s[i];
    }

    // 1) creation of matrix (alfa z) * b = beta
    alfa[1] = y[1];
    beta[1] = s[1];
    for (int i = 2; i <= n; i++) {
        alfa[i] = y[i] - x[i] * z[i - 1] /(double)alfa[i - 1];
        test = alfa[i];
        beta[i] = s[i] - x[i] * beta[i - 1] /(double)alfa[i - 1];
        test = beta[i];
    }

    // 2) creation of b coefficients
    b[n] = beta[n] / alfa[n];
    test = b[n];
    for (int i = n - 1; i >= 1; i--) {
        b[i] = (beta[i] - z[i] * b[i + 1]) /(double)alfa[i];
        test = b[i];
    }
    b[0] = 0;
    test = b[0];

    // 3) creation of a coefficients
    for (int i = 0; i <= n - 1; i++) {
        a[i] = (b[i + 1] - b[i]) /(double)(3 * (x_array[i + 1] - x_array[i]));
        test = a[i];
    }
    a[n] = -b[n] /(double)(3 * (x_array[n + 1] - x_array[n]));
    test = a[n];

    // 4) creation of c coefficients
    for (int i = 0; i <= n; i++) {
        c[i] = (y_array[i + 1] - y_array[i]) /(double)(x_array[i + 1] - x_array[i]) -
                b[i] * (x_array[i + 1] - x_array[i]) -
                a[i] * (x_array[i + 1] - x_array[i]) * (x_array[i + 1] - x_array[i]);
        test = c[i];
    }
    free(alfa);
    free(beta);
    free(x);
    free(y);
    free(z);
    free(s);
}

void create_new_lines(short* array, int width, int amount_lines, int amount_points,
                        short* base_points_y, short* base_points_x) {
    double* a = (double*)malloc(4 * (amount_points + 1) * (amount_lines + 1) * sizeof(double));
    double* b = (double*)malloc(4 * (amount_points + 1) * (amount_lines + 1) * sizeof(double));
    double* c = (double*)malloc(4 * (amount_points + 1) * (amount_lines + 1) * sizeof(double));
    short x1, x2;
    short test;

    // 0)creation of cubic splines
    for (int i = 0; i < amount_lines; i++) {
        calculation_coefficients_cubic_spline(base_points_y + i * amount_points, base_points_x + i * amount_points,
                                              amount_points, a, b, c);
        for (int j = 0; j < amount_points - 1; j++) {
            x1 = base_points_x[i * amount_points + j];
            x2 = base_points_x[i * amount_points + j + 1];
            for (short k = x1; k < x2; k++) {
                array[i * width + k] = (short)(a[j] * (k - x1) * (k - x1) * (k - x1) +
                                                b[j] * (k - x1) * (k - x1) + c[j] * (k - x1) +
                                                base_points_y[i * amount_points + j]);
                test = array[i * width + k];
            }
        }
    }
    free(a);
    free(b);
    free(c);
}
