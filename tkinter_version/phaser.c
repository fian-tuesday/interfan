#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <math.h>

void create_phase1(int width, int height, short* lines, int amount_lines, double* phase) {
    short y1, y2;
    double pi = 3.14;

    // 0) the phase between y = 0 and y = line[0] is 0
     for (int i = 0; i < width; i++) {
        for (int j = 0; j < lines[i]; j++) {
            phase[i * height + j] = 0;
        }
     }

     // 1) the phase between line[0] and line[amount_lines - 1] increases linearly
     for (int i = 0; i < width; i++) {
        for (int j = 0; j < amount_lines - 1; j++) {
            y1 = lines[j * width + i];
            y2 = lines[(j + 1) * width + i];
            for (short y = y1; y <= y2; y++) {
                phase[i * height + y] = (double)(pi * j + pi * (y - y1) / (double)(y2 - y1));
            }
        }
     }

     // 2) the phase between line[amount_lines - 1] and y = height - 1 is constant
     for (int i = 0; i < width; i++) {
        for (short y = lines[(amount_lines - 1) * width + i]; y < height; y++) {
            phase[i * height + y] = phase[i * height + lines[(amount_lines - 1) * width + i]];
        }
     }
 }

void calculation_coefficients_cubic_spline (double* y_array, short* x_array, int amount_points,
                                            double* a, double* b, double* c) {
    double* alfa = (double*)malloc(4 * amount_points * sizeof(double));
    double* beta = (double*)malloc(4 * amount_points * sizeof(double));
    double* x = (double*)malloc(4 * amount_points * sizeof(double));
    double* y = (double*)malloc(4 * amount_points * sizeof(double));
    double* z = (double*)malloc(4 * amount_points * sizeof(double));
    double* s = (double*)malloc(4 * amount_points * sizeof(double));
    int n = amount_points - 2;

    // 0) creation of matrix (xyz) * b = s
    for (int i = 1; i <= n; i++) {
        x[i] = x_array[i] - x_array[i - 1];
        y[i] = 2 * (x_array[i + 1] - x_array[i - 1]);
        z[i] = x_array[i + 1] - x_array[i];
        s[i] = 3 * ((y_array[i + 1] - y_array[i]) /(double)(x_array[i + 1] - x_array[i]) -
               (y_array[i] - y_array[i - 1]) /(double)(x_array[i] - x_array[i - 1]));
    }

    // 1) creation of matrix (alfa z) * b = beta
    alfa[1] = y[1];
    beta[1] = s[1];
    for (int i = 2; i <= n; i++) {
        alfa[i] = y[i] - x[i] * z[i - 1] /(double)alfa[i - 1];
        beta[i] = s[i] - x[i] * beta[i - 1] /(double)alfa[i - 1];
    }

    // 2) creation of b coefficients
    b[n] = beta[n] / alfa[n];
    for (int i = n - 1; i >= 1; i--) {
        b[i] = (beta[i] - z[i] * b[i + 1]) /(double)alfa[i];
    }
    b[0] = 0;

    // 3) creation of a coefficients
    for (int i = 0; i <= n - 1; i++) {
        a[i] = (b[i + 1] - b[i]) /(double)(3 * (x_array[i + 1] - x_array[i]));
    }
    a[n] = -b[n] /(double)(3 * (x_array[n + 1] - x_array[n]));

    // 4) creation of c coefficients
    for (int i = 0; i <= n; i++) {
        c[i] = (y_array[i + 1] - y_array[i]) /(double)(x_array[i + 1] - x_array[i]) -
                b[i] * (x_array[i + 1] - x_array[i]) -
                a[i] * (x_array[i + 1] - x_array[i]) * (x_array[i + 1] - x_array[i]);
    }
    free(alfa);
    free(beta);
    free(x);
    free(y);
    free(z);
    free(s);

}

void create_phase2(int width, int height, short* lines, int amount_lines, double* phase) {
    short y1, y2;
    double pi = 3.14;
    short* array_x = (short*)malloc(4 * (amount_lines + 1) * sizeof(short));
    double* array_y = (double*)malloc(4 * (amount_lines + 1) * sizeof(double));
    double* a = (double*)malloc(4 * (amount_lines + 3) * sizeof(double));
    double* b = (double*)malloc(4 * (amount_lines + 3) * sizeof(double));
    double* c = (double*)malloc(4 * (amount_lines + 3) * sizeof(double));

    /*// 0) the phase between y = 0 and y = line[0] is 0
    for (int i = 0; i < width; i++) {
       for (int j = 0; j < lines[i]; j++) {
           phase[i * height + j] = 0;
       }
    }*/
    // 1) calculating  phase between lines
    for (int i = 0; i < width; i++) {
        // 1.1) creating array_x and array_y
        array_x[0] = 0;
        array_y[0] = 0;
        for (int j = 0; j < amount_lines; j++) {
            array_x[j + 1] = lines[j * width + i];
            array_y[j + 1] = (double)pi * (j + 1);
        }
        array_x[amount_lines + 1] = height - 1;
        array_y[amount_lines + 1] = (amount_lines + 1) * pi;

        // 1.2) calculating phase
        calculation_coefficients_cubic_spline(array_y, array_x, amount_lines + 2, a, b, c);
        for (int j = 0; j < amount_lines - 1; j++) {
            y1 = lines[j * width + i];
            y2 = lines[(j + 1) * width + i];
            for (short y = y1; y < y2; y++) {
                phase[i * height + y] = (double)(a[j] * (y - y1) * (y - y1) * (y - y1) +
                                                 b[j] * (y - y1) * (y - y1) + c[j] * (y - y1) + pi * j);
            }
        }
    }

    /*// 2) the phase between line[amount_lines - 1] and y = height - 1 is constant
    for (int i = 0; i < width; i++) {
       for (short y = lines[(amount_lines - 1) * width + i]; y < height; y++) {
           phase[i * height + y] = phase[i * height + lines[(amount_lines - 1) * width + i]];
       }
    }*/
    free(array_x);
    free(array_y);
    free(a);
    free(b);
    free(c);
}

void calculate_phase_difference(int width, int height, double* unchanged_phase,
                                double* changed_phase, short* phase_difference) {
    double pi = 3.14;

    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            phase_difference[i * height + j] = (short)((changed_phase[i * height + j] -
                                                        unchanged_phase[i * height + j]) * 256 / (double)(2 * pi));
        }
    }
}
