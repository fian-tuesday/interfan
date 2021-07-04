#!/usr/bin/env python
import base_points_finder
import numpy as np
import os.path
from PIL import Image


image_filename = r'int_0_clr_still.tif'
data_folder = r'data'


def main():
    input_image_filename = os.path.join(data_folder, image_filename)
    input_image = Image.open(input_image_filename)
    print('Opened image', input_image_filename, 'with size', input_image.size, 'and mode', input_image.mode)
    assert input_image.mode in ('RGB', 'RGBA'), "No support for other color modes than RGB and RGBA."
    image_data = input_image.getdata()
    # Зелёный в данной картинке всегда средний по яркости - берём именно его
    brightness = np.array(list(components[1] for components in image_data)).reshape(input_image.size[::-1])

    black_base_points, white_base_points = base_points_finder.get_all_base_points(brightness)

    output_image_data = list(image_data)
    for x, y in white_base_points:
        output_image_data[y * input_image.width + x] = (255, 0, 0)
    for x, y in black_base_points:
        output_image_data[y * input_image.width + x] = (0, 0, 255)
    output_image = Image.new(input_image.mode, input_image.size)
    output_image.putdata(output_image_data)
    output_image_filename = os.path.join(data_folder, image_filename.replace('.tif', '_basepoints.tif'))
    output_image.save(output_image_filename)
    print(f'Saved image with base points: {output_image_filename}')


if __name__ == "__main__":
    main()
