# coding: utf-8

import keyword


def hello():
    print('Hello Python!')


def test_keyword():
    keywords = keyword.kwlist
    print(keywords)
    print(f'len(keywords): {len(keywords)}')


if __name__ == '__main__':
    pass
    test_keyword()
