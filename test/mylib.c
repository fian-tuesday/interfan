#include "mylib.h"

void my_eraser(void *pointer)
{
   long int *array = (long int*)pointer;
   for(int i = 0; i < 50; i++)
       array[i] = 0;
}
