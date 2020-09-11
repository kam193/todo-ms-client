from datetime import datetime

import pytest
from dateutil import tz

from todoms.attributes import Importance, Status
from todoms.filters import and_, eq, ge, gt, le, lt, ne, or_

comparable_example_values = [
    ("value", "'value'"),
    (Importance.LOW, "'low'"),
    (Status.COMPLETED, "'completed'"),
    (datetime(2020, 1, 1, 18, tzinfo=tz.UTC), "2020-01-01T18:00:00Z"),
    (True, "true"),
    (False, "false"),
]


def test_and_args():
    assert and_("test_1", "test_2") == "(test_1 and test_2)"


def test_and_kwargs():
    assert and_(a="b", c="d") == "(a b and c d)"


@pytest.mark.parametrize(
    "args,kwargs,expected",
    [
        (["test_1", "test_2"], {}, "(test_1 and test_2)"),
        ([], {"a": "b", "c": "d"}, "(a b and c d)"),
        (["condition"], {}, "condition"),
        ([], {"b": "e"}, "b e"),
        (
            ["c_1", "c_2", "c_3"],
            {"v1": "t1", "v2": "t2", "v3": "t3"},
            "(c_1 and c_2 and c_3 and v1 t1 and v2 t2 and v3 t3)",
        ),
    ],
)
def test_and_(args, kwargs, expected):
    assert and_(*args, **kwargs) == expected


@pytest.mark.parametrize(
    "args,kwargs,expected",
    [
        (["test_1", "test_2"], {}, "(test_1 or test_2)"),
        ([], {"a": "b", "c": "d"}, "(a b or c d)"),
        (["condition"], {}, "condition"),
        ([], {"b": "e"}, "b e"),
        (
            ["c_1", "c_2", "c_3"],
            {"v1": "t1", "v2": "t2", "v3": "t3"},
            "(c_1 or c_2 or c_3 or v1 t1 or v2 t2 or v3 t3)",
        ),
    ],
)
def test_or_(args, kwargs, expected):
    assert or_(*args, **kwargs) == expected


@pytest.mark.parametrize("value,expected_text", comparable_example_values)
def test_eq(value, expected_text):
    assert eq(value) == f"eq {expected_text}"


@pytest.mark.parametrize("value,expected_text", comparable_example_values)
def test_ne(value, expected_text):
    assert ne(value) == f"ne {expected_text}"


@pytest.mark.parametrize("value,expected_text", comparable_example_values)
def test_gt(value, expected_text):
    assert gt(value) == f"gt {expected_text}"


@pytest.mark.parametrize("value,expected_text", comparable_example_values)
def test_ge(value, expected_text):
    assert ge(value) == f"ge {expected_text}"


@pytest.mark.parametrize("value,expected_text", comparable_example_values)
def test_le(value, expected_text):
    assert le(value) == f"le {expected_text}"


@pytest.mark.parametrize("value,expected_text", comparable_example_values)
def test_lt(value, expected_text):
    assert lt(value) == f"lt {expected_text}"
