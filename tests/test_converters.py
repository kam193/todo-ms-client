from datetime import datetime, timezone, timedelta
from dateutil import tz
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


def test_default_converter_back_returns_input():
    attr_converter = AttributeConverter("original", "new name")
    data = Mock()

    assert attr_converter.back_converter(data) == data


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


def test_datetime_attr_converter_back():
    converter = DatetimeAttrConverter("", "")
    data = datetime(2020, 5, 21, 15, tzinfo=tz.UTC)

    result = converter.back_converter(data)

    expected = {"dateTime": "2020-05-21T15:00:00.000000", "timeZone": "UTC"}

    assert expected == result


@mark.parametrize("data", [{}, None])
def test_datetime_attr_converter_back_when_no_data(data):
    converter = DatetimeAttrConverter("", "")
    assert converter.back_converter(data) is None


@mark.parametrize("data", [{}, None])
def test_content_attr_converter_when_no_data(data):
    converter = ContentAttrConverter("", "")
    assert converter.obj_converter(data) == ""


def test_content_attr_converter():
    converter = ContentAttrConverter("", "")
    data = {"content": "The description"}
    assert converter.obj_converter(data) == "The description"


def test_content_attr_converter_back():
    converter = ContentAttrConverter("", "")
    expected = {"content": "The description", "contentType": "html"}
    assert converter.back_converter("The description") == expected


def test_isotime_attr_converter():
    converter = IsoTimeAttrConverter("", "")
    data = "2020-01-01T18:00:00Z"
    expected_time = datetime(2020, 1, 1, 18, tzinfo=timezone.utc)

    assert converter.obj_converter(data) == expected_time


def test_isotime_attr_converter_back():
    converter = IsoTimeAttrConverter("", "")
    data = datetime(2020, 1, 1, 18, tzinfo=tz.gettz("UTC+2"))
    assert converter.back_converter(data) == "2020-01-01T16:00:00Z"
