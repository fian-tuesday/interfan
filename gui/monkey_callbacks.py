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
        data,
        number_of_approximation_points: range(10, 100, 5) = 45,
        lower_threshold: range(256) = 100,
        upper_threshold: range(256) = 100
):
    """
    Определение точек

    Description

    :param data: input_data
    :param number_of_approximation_points: Количество точек аппроксимации
    :param lower_threshold: Порог, ниже которого локальный минимум считаем черной полосой
    :param upper_threshold: Порог, выше которого локальный максимум считаем белой полосой
    """
    pass


# noinspection PyTypeHints, PyUnusedLocal
@monkey_decorator
def trace_interference_lines(data, arg1: bool = True, arg2: bool = False, arg3: int = 10):
    """
    Определение линий

    Подробное описание

    :param data: input_data
    :param arg1: Какой-то параметр
    :param arg2: Еще какой-то параметр с очень очень длинным названием
    :param arg3: Кокое-то произвольное число
    """
    pass


# noinspection PyTypeHints, PyUnusedLocal
@monkey_decorator
def calculate_phases(data, arg0='Hello world'):
    """
    Определение фаз

    :param data: input_data
    :param arg0: Текстовый параметр
    """
    pass
