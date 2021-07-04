from PIL import Image

from monkey_callbacks import monkey_decorator


@monkey_decorator
def visualize_base_points(base_points) -> Image:
    return Image.open('int_0_clr_still_base.tiff')


@monkey_decorator
def visualize_interference_lines(lines) -> Image:
    return Image.open('int_0_clr_still_trace.tiff')


@monkey_decorator
def visualize_phases(phases) -> Image:
    return Image.open('int_0_clr_still_phase.tiff')
