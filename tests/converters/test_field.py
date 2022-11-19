import pytest

from todoms.convertable import BaseConvertableFieldsObject
from todoms.converters import BaseConverter
from todoms.converters.field import (
    Attribute,
    Content,
    Date,
    Datetime,
    Field,
    ImportanceField,
    IsoTime,
    StatusField,
)


@pytest.fixture
def prepare_container():
    def _prepare_container(field_class):
        class FieldContainer(BaseConvertableFieldsObject):
            field = field_class("old")

        return FieldContainer()

    return _prepare_container


class DummyConverter(BaseConverter):
    @classmethod
    def obj_converter(cls, data):
        return f"some_object+{data}"

    @classmethod
    def back_converter(cls, data):
        return f"some_back+{data}"


class DummyField(Field):
    _converter = DummyConverter


class ExampleClass:
    f1 = DummyField("f1")
    f2 = DummyField("another_name")


class TestField:
    def test_crud_field(self):
        obj = ExampleClass()
        obj.f1 = 1

        assert obj.f1 == 1
        assert obj.f2 is None

        obj.f1 = 2
        assert obj.f1 == 2

    def test_field_from_dict_uses_converter(self):
        obj = ExampleClass()

        ExampleClass.f1.from_dict(obj, {"f1": 1, "another_name": 2})
        ExampleClass.f2.from_dict(obj, {"f1": 1, "another_name": 2})

        assert obj.f1 == "some_object+1"
        assert obj.f2 == "some_object+2"

    def test_field_from_dict_with_none(self):
        obj = ExampleClass()

        ExampleClass.f1.from_dict(obj, {"another_name": 2})
        ExampleClass.f2.from_dict(obj, {"f1": 1})

        assert obj.f1 is None
        assert obj.f2 is None

    @pytest.mark.parametrize("data", [{}, None])
    def test_datetime_to_dict_when_no_data(self, data):
        obj = ExampleClass()
        obj.f1 = data
        assert ExampleClass.f1.to_dict(obj) == {"f1": None}

    def test_field_to_dict_uses_converter(self):
        obj = ExampleClass()
        obj.f1 = 1
        obj.f2 = 2

        assert ExampleClass.f1.to_dict(obj) == {"f1": "some_back+1"}
        assert ExampleClass.f2.to_dict(obj) == {"another_name": "some_back+2"}


class TestCommonBehavior:
    field_classes = [
        Attribute,
        Datetime,
        Content,
        IsoTime,
        Date,
        ImportanceField,
        StatusField,
    ]

    def get_container_class(self, field_class):
        class FieldContainer(BaseConvertableFieldsObject):
            field = field_class("old")

        return FieldContainer

    def from_dict(self, data, field_class):
        obj = self.get_container_class(field_class).from_dict({"old": data})
        return obj.field

    def to_dict(self, data, field_class):
        obj = self.get_container_class(field_class)()
        obj.field = data
        return obj.to_dict()["old"]

    @pytest.mark.parametrize("field_class", field_classes)
    @pytest.mark.parametrize("data", [{}, None])
    def test_field_from_dict_when_no_data(self, data, field_class):
        assert self.from_dict(data, field_class) is None

    @pytest.mark.parametrize("field_class", field_classes)
    @pytest.mark.parametrize("data", [{}, None])
    def test_datetime_to_dict_when_no_data(self, data, field_class):
        assert self.to_dict(data, field_class) is None
