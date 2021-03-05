#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <math.h>

void correction_mask(int point, int length, int radius, int* x1, int* x2) {
    if (point < radius) {
        *x1 = radius - point;
        *x2 = 2 * radius;
    }
    else if (length - 1 - point < radius) {
        *x1 = 0;
        *x2 = radius + length - point - 1;
    }
    else {
        *x1 = 0;
        *x2 = 2 * radius;
    }
}

void line_filtration(int* array, int width, int height, double* mask, int radius, int* result) {
    int side = 2 * radius + 1;
    int x1 = 0, x2 = 0, y1 = 0, y2 = 0, test, k = 0;
    double sum, sum_elements = 0;
    int* right_array = (int*)malloc(4 * (width + 1) * (height + 1) * sizeof(int));

    // 0)the transpose of an array
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            right_array[k] = array[j * width + i];
            k++;
        }
    }

    // 1) filtration
    for (int i = 0; i < height; i++) {
        correction_mask(i, height, radius, &y1, &y2);
        for (int j = 0; j < width; j++) {
            correction_mask(j, width, radius, &x1, &x2);
            sum = 0.0;
            sum_elements = 0.0;
            for (int y = y1; y <= y2; y++) {
                for (int x = x1; x <= x2; x++) {
                    sum = sum + mask[y * side + x] * right_array[(i - radius + y) * width + j - radius + x];
                    sum_elements = sum_elements + mask[y * side + x];
                }
            }
            result[i *width + j] = (int)(sum / (double)sum_elements);
        }
    }
    free(right_array);
}

void test_load_image(int* array, int width, int height) {
    FILE* output = fopen("test_load_image_c.txt", "w");
    int* right_array = (int*)malloc(4 * (width + 1) * (height + 1) * sizeof(int));
    int k = 0;

    /*//0)the transpose of an array
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            right_array[k] = array[j * width + i];
            k++;
        }
    }*/
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            fprintf(output, "%d\n", array[i * height + j]);
        }
    }
    fclose(output);
}

void creating_gaussian_matrix(int radius, double dispersion1, double dispersion2, double* mask) {
    int side = 2 * radius + 1;

    for (int i = 0; i < side; i++) {
        for (int j = 0; j < side; j++) {
            mask[i * side + j] = exp(-0.5 * ((i - radius) * (i - radius) / dispersion1 +
                                             (j - radius) * (j - radius) / dispersion2));
        }
    }

}
