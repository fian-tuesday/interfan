from functools import wraps


def monkey_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'{func.__name__}({", ".join(map(str, args))}'
              f'{", " + ", ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""})')
        return func(*args, **kwargs)
    wrapper.__defaults__ = func.__defaults__
    return wrapper


# noinspection PyTypeHints, PyUnusedLocal
@monkey_decorator
def get_base_points(
        brightness_array,
        number_of_approximation_points: range(10, 100, 5) = 45,
        lower_threshold: range(256) = 100,
        upper_threshold: range(256) = 100
):
    """
    Определение точек

    Description

    :param brightness_array: input_data
    :param range(10, 100, 5) number_of_approximation_points: Количество точек аппроксимации default 45
    :param range(256) lower_threshold: Порог, ниже которого локальный минимум считаем черной полосой default 100
    :param range(256) upper_threshold: Порог, выше которого локальный максимум считаем белой полосой default 100
    """
    return True


# noinspection PyTypeHints, PyUnusedLocal
@monkey_decorator
def trace_interference_lines(data, arg1: bool = True, arg2: bool = False, arg3: int = 10):
    """
    Определение линий

    Подробное описание

    :param data: input_data
    :param bool arg1: Какой-то параметр default True
    :param bool arg2: Еще какой-то параметр с очень очень длинным названием default False
    :param int arg3: Кокое-то произвольное число default 10
    """
    return True


# noinspection PyTypeHints, PyUnusedLocal
@monkey_decorator
def calculate_phases(data, arg0='Hello world'):
    """
    Определение фаз

    :param data: input_data
    :param str arg0: Текстовый параметр default 'Hello world'
    """
    return True
