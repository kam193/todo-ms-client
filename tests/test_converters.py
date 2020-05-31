from datetime import datetime, timezone
from unittest.mock import Mock

from pytest import mark

from todoms.converters import (
    AttributeConverter,
    DatetimeAttrConverter,
    ContentAttrConverter,
    IsoTimeAttrConverter,
)


def test_default_converter_returns_input():
    attr_converter = AttributeConverter("original", "new name")
    data = Mock()

    assert attr_converter.obj_converter(data) == data


def test_datetime_attr_converter_from():
    converter = DatetimeAttrConverter("", "")
    data = {"dateTime": "2020-05-21T10:00:00.0000000", "timeZone": "America/Bogota"}

    result = converter.obj_converter(data)

    expected_utc = datetime(2020, 5, 21, 15, tzinfo=timezone.utc)
    result_utc = result.astimezone(timezone.utc)

    assert expected_utc == result_utc


@mark.parametrize("data", [{}, None])
def test_datetime_attr_converter_when_no_data(data):
    converter = DatetimeAttrConverter("", "")
    assert converter.obj_converter(data) is None


@mark.parametrize("data", [{}, None])
def test_content_attr_converter_when_no_data(data):
    converter = ContentAttrConverter("", "")
    assert converter.obj_converter(data) == ""


def test_content_attr_converter():
    converter = ContentAttrConverter("", "")
    data = {"content": "The description"}
    assert converter.obj_converter(data) == "The description"


def test_isotime_attr_converter():
    converter = IsoTimeAttrConverter("", "")
    data = "2020-01-01T18:00:00Z"
    expected_time = datetime(2020, 1, 1, 18, tzinfo=timezone.utc)

    assert converter.obj_converter(data) == expected_time
