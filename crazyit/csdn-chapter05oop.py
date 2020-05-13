# coding: utf-8

from inspect import ismethod, isfunction
from datetime import datetime


def log_parameter_decorator(fn):
    # print(f"{'-' * 60}log_parameter_decorator")

    def log_parameter(*args):
        # print(f"{'-' * 60}log_parameter")
        fn_type = 'method' if ismethod(fn) else 'function'
        print(f"Enter {fn_type} {fn.__name__}(), args is {args}.")

        result = fn(*args)

        print(f'Exit {fn_type} {fn.__name__}().')
        return result

    return log_parameter


def log_elapse_decorator(fn):
    # print(f"{'-' * 60}log_time_decorator")

    def log_time(*args):
        print(f"{'-' * 60}log_time")
        enter_time = datetime.now()
        print(f"Enter time is {enter_time}")

        result = fn(*args)

        print(f'Exit time is {datetime.now()}, elapse {datetime.now() - enter_time}')
        return result

    return log_time


def test_function():
    print(f"{'-' * 60}test_function")
    func = log_parameter_decorator
    # for proper in dir(func):
    #     print(f'{proper}: {func.__getattribute__(proper)}')
    print(ismethod(func))
    print(isfunction(func))


@log_elapse_decorator
@log_parameter_decorator
def add(a, b):
    # print(f"{'-' * 60}add")
    return sum([a, b])


if __name__ == '__main__':
    print(f"{'-' * 60}main")
    print(add(1, 2))
    # test_function()
