# coding: utf-8

from inspect import ismethod, isfunction


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


def test_function():
    print(f"{'-' * 60}test_function")
    func = log_parameter_decorator
    # for proper in dir(func):
    #     print(f'{proper}: {func.__getattribute__(proper)}')
    print(ismethod(func))
    print(isfunction(func))


@log_parameter_decorator
def add(a, b):
    # print(f"{'-' * 60}add")
    return sum([a, b])


if __name__ == '__main__':
    print(f"{'-' * 60}main")
    print(add(1, 2))
    # test_function()
