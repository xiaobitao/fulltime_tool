"""The core_tests module consists of tests (based on pytest)
on various functions in the core module.
"""

from datetime import date, datetime, time

from .core import list_files, load_data

import timeit

import pytest


def test_datetime_format():
    dt_str = '2019-07-15 00:00'
    fmt = "%Y-%m-%d %H:%M"
    dt_obj = datetime.strptime(dt_str, fmt)
    assert dt_obj.date().year == 2019
    assert dt_obj.time().minute == 0

def test_list_files():
    list_files('p0', '2019-07-15 00:00', 5)


def test_load_data():
    data = load_data('p0', '2019-07-15 00:00', 2, 527)
    r, c = data.shape
    one_minute = 1000*60

    assert c == 527
    assert r/one_minute > 2

    