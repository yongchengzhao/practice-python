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
