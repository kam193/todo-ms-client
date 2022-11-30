from datetime import date, datetime, timezone
from enum import Enum
from unittest.mock import Mock

import pytest
from dateutil import tz

from todoms.attributes import Content, ContentType
from todoms.converters.basic import (
    AttributeConverter,
    ContentConverter,
    DateConverter,
    DatetimeConverter,
    EnumConverter,
    IsoTimeConverter,
    ListConverter,
)


class TestAttributeConverter:
    def test_default_converter_returns_input(self):
        attr_converter = AttributeConverter()
        data = Mock()

        assert attr_converter.obj_converter(data) == data

    def test_default_converter_back_returns_input(self):
        attr_converter = AttributeConverter()
        data = Mock()

        assert attr_converter.back_converter(data) == data


class TestDatetimeConverter:
    def test_datetime_converter_from(self):
        converter = DatetimeConverter()
        data = {"dateTime": "2020-05-21T10:00:00.0000000", "timeZone": "America/Bogota"}

        result = converter.obj_converter(data)

        expected_utc = datetime(2020, 5, 21, 15, tzinfo=timezone.utc)
        result_utc = result.astimezone(timezone.utc)

        assert expected_utc == result_utc

    @pytest.mark.parametrize("data", [{}, None])
    def test_datetime_converter_when_no_data(self, data):
        converter = DatetimeConverter()
        assert converter.obj_converter(data) is None

    def test_datetime_converter_back(self):
        converter = DatetimeConverter()
        data = datetime(2020, 5, 21, 15, tzinfo=tz.UTC)

        result = converter.back_converter(data)

        expected = {"dateTime": "2020-05-21T15:00:00.000000", "timeZone": "UTC"}

        assert expected == result

    @pytest.mark.parametrize("data", [{}, None])
    def test_datetime_converter_back_when_no_data(self, data):
        converter = DatetimeConverter()
        assert converter.back_converter(data) is None


class TestContentConverter:
    @pytest.mark.parametrize("data", [{}, None])
    def test_content_converter_when_no_data(self, data):
        converter = ContentConverter()
        assert converter.obj_converter(data) == Content(None, ContentType.HTML)

    @pytest.mark.parametrize("type", [ContentType.HTML, ContentType.TEXT])
    def test_content_converter(self, type):
        converter = ContentConverter()
        data = {"content": "The description", "contentType": type.value}
        assert converter.obj_converter(data) == Content("The description", type)

    def test_content_converter_back_html(self):
        converter = ContentConverter()
        data = Content("The description", ContentType.HTML)
        expected = {"content": "The description", "contentType": "html"}
        assert converter.back_converter(data) == expected

    def test_content_converter_back_text(self):
        converter = ContentConverter()
        data = Content("The description", ContentType.TEXT)
        expected = {"content": "The description", "contentType": "text"}
        assert converter.back_converter(data) == expected

    @pytest.mark.parametrize("data", [None, Content(None, ContentType.HTML)])
    def test_content_converter_back_when_no_data(self, data):
        converter = ContentConverter()
        expected = {"content": None, "contentType": "html"}
        assert converter.back_converter(data) == expected


class TestIsoTimeConverter:
    def test_isotime_converter(self):
        converter = IsoTimeConverter()
        data = "2020-01-01T18:00:00Z"
        expected_time = datetime(2020, 1, 1, 18, tzinfo=timezone.utc)

        assert converter.obj_converter(data) == expected_time

    def test_isotime_converter_back(self):
        converter = IsoTimeConverter()
        data = datetime(2020, 1, 1, 18, tzinfo=tz.gettz("UTC+2"))
        assert converter.back_converter(data) == "2020-01-01T16:00:00Z"

    def test_isotime_converter_back_when_no_data(self):
        converter = IsoTimeConverter()
        assert converter.back_converter(None) is None


class TestDateConverter:
    def test_date_converter(self):
        converter = DateConverter()
        data = "2020-01-01"
        expected_time = date(2020, 1, 1)

        assert converter.obj_converter(data) == expected_time

    def test_date_converter_back(self):
        converter = DateConverter()
        data = date(2020, 1, 1)
        assert converter.back_converter(data) == "2020-01-01"

    def test_date_converter_back_when_no_data(self):
        converter = DateConverter()
        assert converter.back_converter(None) is None


class ExampleEnum(Enum):
    VAL_1 = "val1"
    VAL_2 = "val2"


@pytest.fixture
def enum_converter():
    return EnumConverter(enum=ExampleEnum)


class TestEnumConverter:
    @pytest.mark.parametrize(
        "data,expected",
        [("val1", ExampleEnum.VAL_1), ("val2", ExampleEnum.VAL_2), (None, None)],
    )
    def test_enum_converter(self, enum_converter, data, expected):
        assert enum_converter.obj_converter(data) == expected

    @pytest.mark.parametrize(
        "data,expected",
        [(ExampleEnum.VAL_1, "val1"), (ExampleEnum.VAL_2, "val2"), (None, None)],
    )
    def test_enum_back_converter(self, enum_converter, data, expected):
        assert enum_converter.back_converter(data) == expected


class TestListConverter:
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
