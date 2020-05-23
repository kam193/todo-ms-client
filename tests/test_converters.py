from datetime import datetime, timezone
from unittest.mock import Mock

from pytest import mark

from todoms.converters import (
    AttributeConverter,
    content_converter,
    datetime_dict_converter,
)


def test_default_converter_returns_input():
    attr_converter = AttributeConverter("original", "new name")
    data = Mock()

    assert attr_converter.obj_converter(data) == data


def test_datetime_from_dict_converter():
    data = {"dateTime": "2020-05-21T10:00:00.0000000", "timeZone": "America/Bogota"}

    result = datetime_dict_converter(data)

    expected_utc = datetime(2020, 5, 21, 15, tzinfo=timezone.utc)
    result_utc = result.astimezone(timezone.utc)

    assert expected_utc == result_utc


@mark.parametrize("data", [{}, None])
def test_datetime_from_dict_converter_when_no_data(data):
    assert datetime_dict_converter(data) is None


def test_content_converter():
    data = {"content": "The description"}
    assert content_converter(data) == "The description"


@mark.parametrize("data", [{}, None])
def test_content_converter_when_no_data(data):
    assert content_converter(data) == ""
