from datetime import date, datetime, timezone
from enum import Enum
from unittest.mock import Mock

import pytest
from dateutil import tz

from todoms.converters.basic import (
    AttributeConverter,
    ContentAttrConverter,
    DateAttrConverter,
    DatetimeAttrConverter,
    EnumAttrConverter,
    IsoTimeAttrConverter,
    ListConverter,
)


class TestAttributeConverter:
    def test_default_converter_returns_input(self):
        attr_converter = AttributeConverter("original", "new name")
        data = Mock()

        assert attr_converter.obj_converter(data) == data

    def test_default_converter_back_returns_input(self):
        attr_converter = AttributeConverter("original", "new name")
        data = Mock()

        assert attr_converter.back_converter(data) == data


class TestDatetimeAttrConverter:
    def test_datetime_attr_converter_from(self):
        converter = DatetimeAttrConverter("", "")
        data = {"dateTime": "2020-05-21T10:00:00.0000000", "timeZone": "America/Bogota"}

        result = converter.obj_converter(data)

        expected_utc = datetime(2020, 5, 21, 15, tzinfo=timezone.utc)
        result_utc = result.astimezone(timezone.utc)

        assert expected_utc == result_utc

    @pytest.mark.parametrize("data", [{}, None])
    def test_datetime_attr_converter_when_no_data(self, data):
        converter = DatetimeAttrConverter("", "")
        assert converter.obj_converter(data) is None

    def test_datetime_attr_converter_back(self):
        converter = DatetimeAttrConverter("", "")
        data = datetime(2020, 5, 21, 15, tzinfo=tz.UTC)

        result = converter.back_converter(data)

        expected = {"dateTime": "2020-05-21T15:00:00.000000", "timeZone": "UTC"}

        assert expected == result

    @pytest.mark.parametrize("data", [{}, None])
    def test_datetime_attr_converter_back_when_no_data(self, data):
        converter = DatetimeAttrConverter("", "")
        assert converter.back_converter(data) is None


class TestContentAttrConverter:
    @pytest.mark.parametrize("data", [{}, None])
    def test_content_attr_converter_when_no_data(self, data):
        converter = ContentAttrConverter("", "")
        assert converter.obj_converter(data) == ""

    def test_content_attr_converter(self):
        converter = ContentAttrConverter("", "")
        data = {"content": "The description"}
        assert converter.obj_converter(data) == "The description"

    def test_content_attr_converter_back(self):
        converter = ContentAttrConverter("", "")
        expected = {"content": "The description", "contentType": "html"}
        assert converter.back_converter("The description") == expected

    def test_content_attr_converter_back_when_no_data(self):
        converter = ContentAttrConverter("", "")
        expected = {"content": None, "contentType": "html"}
        assert converter.back_converter(None) == expected


class TestIsoTimeAttrConverter:
    def test_isotime_attr_converter(self):
        converter = IsoTimeAttrConverter("", "")
        data = "2020-01-01T18:00:00Z"
        expected_time = datetime(2020, 1, 1, 18, tzinfo=timezone.utc)

        assert converter.obj_converter(data) == expected_time

    def test_isotime_attr_converter_back(self):
        converter = IsoTimeAttrConverter("", "")
        data = datetime(2020, 1, 1, 18, tzinfo=tz.gettz("UTC+2"))
        assert converter.back_converter(data) == "2020-01-01T16:00:00Z"

    def test_isotime_attr_converter_back_when_no_data(self):
        converter = IsoTimeAttrConverter("", "")
        assert converter.back_converter(None) is None


class TestDateAttrConverter:
    def test_date_attr_converter(self):
        converter = DateAttrConverter("", "")
        data = "2020-01-01"
        expected_time = date(2020, 1, 1)

        assert converter.obj_converter(data) == expected_time

    def test_date_attr_converter_back(self):
        converter = DateAttrConverter("", "")
        data = date(2020, 1, 1)
        assert converter.back_converter(data) == "2020-01-01"

    def test_date_attr_converter_back_when_no_data(self):
        converter = DateAttrConverter("", "")
        assert converter.back_converter(None) is None


class ExampleEnum(Enum):
    VAL_1 = "val1"
    VAL_2 = "val2"


@pytest.fixture
def enum_converter():
    class ExampleEnumConverter(EnumAttrConverter):
        _ENUM = ExampleEnum

    return ExampleEnumConverter("", "")


class TestEnumAttrConverter:
    @pytest.mark.parametrize(
        "data,expected",
        [("val1", ExampleEnum.VAL_1), ("val2", ExampleEnum.VAL_2), (None, None)],
    )
    def test_enum_attr_converter(self, enum_converter, data, expected):
        assert enum_converter.obj_converter(data) == expected

    @pytest.mark.parametrize(
        "data,expected",
        [(ExampleEnum.VAL_1, "val1"), (ExampleEnum.VAL_2, "val2"), (None, None)],
    )
    def test_enum_attr_back_converter(self, enum_converter, data, expected):
        assert enum_converter.back_converter(data) == expected


class TestListConverter:
    def test_list_converter_proxy_attribute_names(self):
        converter = ListConverter(AttributeConverter("original", "local"))

        assert converter.original_name == "original"
        assert converter.local_name == "local"

    @pytest.mark.parametrize(
        "data,expected",
        [
            (["val1", "val2"], [ExampleEnum.VAL_1, ExampleEnum.VAL_2]),
            (None, None),
            ([], []),
        ],
    )
    def test_list_converter_converts(self, enum_converter, data, expected):
        converter = ListConverter(enum_converter)

        assert converter.obj_converter(data) == expected

    @pytest.mark.parametrize(
        "data,expected",
        [
            ([ExampleEnum.VAL_1, ExampleEnum.VAL_2], ["val1", "val2"]),
            (None, None),
            ([], []),
        ],
    )
    def test_list_converter_back_converting(self, enum_converter, data, expected):
        converter = ListConverter(enum_converter)

        assert converter.back_converter(data) == expected
