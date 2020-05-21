from unittest.mock import Mock
from todoms.converters import AttributeConverter, datetime_dict_converter
from datetime import datetime, timezone


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
