# coding: utf-8

from inspect import ismethod, isfunction
from datetime import datetime
from functools import wraps


def log_parameter(fn):
    # print(f"{'-' * 60}log_parameter_decorator")

    @wraps(fn)
    def decorated(*args):
        # print(f"{'-' * 60}decorated")
        fn_type = 'method' if ismethod(fn) else 'function'
        print(f"Enter {fn_type} {fn.__name__}(), args is {args}.")

        result = fn(*args)

        print(f'Exit {fn_type} {fn.__name__}().')
        return result

    return decorated


def log_elapse(fn):
    """
    耗时装饰器。计算函数或者方法耗时多少。
    :param fn:
    :return:
    """
    # print(f"{'-' * 60}log_time_decorator")

    @wraps(fn)
    def decorated(*args):
        # print(f"{'-' * 60}decorated")
        enter_time = datetime.now()
        print(f"Enter {fn.__name__}(), time is {enter_time}.")

        result = fn(*args)

        exit_time = datetime.now()
        print(f'Exit {fn.__name__}(), time is {exit_time}, elapse {exit_time - enter_time}.')
        del enter_time, exit_time

        return result

    return decorated


class Person:

    def __init__(self, name, code, age):
        self.name = name
        self.code = code
        self.age = age

    def __str__(self):
        return f'[Person ' \
               f'name={self.name}' \
               f', code={self.code}' \
               f', age={self.age}' \
               f']'

    @log_parameter
    @log_elapse
    def walk(self):
        print(f'{self.name} 在走路。')


def test_person():
    p1 = Person('Adam', '002', 20)
    # print(p1)
    print(type(p1.walk))
    print(p1.walk.__class__)
    print(ismethod(p1.walk))
    p1.walk()


def test_function():
    print(f"{'-' * 60}test_function")
    func = log_parameter
    # for proper in dir(func):
    #     print(f'{proper}: {func.__getattribute__(proper)}')
    print(ismethod(func))
    print(isfunction(func))


@log_parameter
@log_elapse
def add(a, b):
    # print(f"{'-' * 60}add")
    return sum([a, b])


if __name__ == '__main__':
    print(f"{'-' * 60}main")
    print(add(1, 2))
    # test_function()
