# coding: utf-8

from datetime import datetime
from functools import wraps


class BaseDecorator:
    __fn = None

    def __init__(self, func):
        self._func = func
        __fn = func

    @wraps(__fn)
    def __call__(self, *args, **kwargs):
        self.enter()
        enter_time = self.enter_time()
        self.log_args(*args, **kwargs)

        result = self._func(*args, **kwargs)

        self.log_result(result)
        self.exit_time(enter_time)
        self.exit()

    def enter(self):
        pass

    def exit(self):
        pass

    @staticmethod
    def enter_time():
        pass

    @staticmethod
    def exit_time(enter_time):
        pass

    @staticmethod
    def log_args(*args, **kwargs):
        pass

    @staticmethod
    def log_result(result):
        pass


class ElapseDecorator(BaseDecorator):

    @staticmethod
    def enter_time():
        print(f'enter_time')
        return datetime.now()

    @staticmethod
    def exit_time(enter_time):
        print(f'exit_time')
        pass


class EnterExitDecorator(BaseDecorator):

    def enter(self):
        print(f'Enter {self._func.__name__}.')

    def exit(self):
        print(f'Exit {self._func.__name__}.')


class LogArgDecorator(BaseDecorator):

    @staticmethod
    def log_args(*args, **kwargs):
        print(f'log_args')
        pass


class LogResultDecorator(BaseDecorator):

    @staticmethod
    def log_result(result):
        print(f'log_result')
        pass


def enter_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'Enter {func.__name__}')
        return func(*args, **kwargs)

    return wrapper


def exit_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'Exit {func.__name__}')
        return result

    return wrapper


def duration(func):
    """
    计算函数耗时装饰器。可以计算“被装饰函数”运行耗时。
    :param func: “被装饰函数”。
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        包装函数，此函数将“被装饰函数”包装成功能更强大的函数。
        :param args: 收集位置参数。
        :param kwargs: 收集关键字参数。
        :return: 返回“被装饰函数”运行结果。
        """
        print(func)
        enter_time = datetime.now()
        # func.__code__.co_filename 为“被装饰函数”所在文件，func.__code__.co_firstlineno 为“被装饰函数”第一行代码的行号。
        enter_info = f'Enter {func.__name__}(), in {func.__code__.co_filename} line {func.__code__.co_firstlineno}.'
        print(enter_info + f' The time is {enter_time}.')

        result = func(*args, **kwargs)

        exit_time = datetime.now()
        print(f'Exit {func.__name__}(), the time is {exit_time}, elapse {exit_time - enter_time}.')

        del enter_time, exit_time
        return result

    return wrapper


def log_args(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'Enter {func.__name__}(), args: {args}.')

        result = func(*args, **kwargs)

        print(f'Exit {func.__name__}(), result: {result}')
        return result

    return wrapper
