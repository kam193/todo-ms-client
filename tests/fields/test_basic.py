from enum import Enum

import pytest

from todoms.attributes import Content, ContentType
from todoms.convertable import BaseConvertableFieldsObject
from todoms.converters import BaseConverter
from todoms.fields.basic import (
    Attribute,
    ContentField,
    Date,
    Datetime,
    EnumField,
    Field,
    IsoTime,
)


class DummyConverter(BaseConverter):
    def obj_converter(self, data):
        return f"some_object+{data}"

    def back_converter(self, data):
        return f"some_back+{data}"


class DummyField(Field):
    _converter = DummyConverter()


class ExampleClass:
    SOME_VALUE = "VAL"
    f1 = DummyField("f1", default="default")
    f2 = DummyField("another_name")
    f3 = DummyField(
        "add_val", post_convert=lambda instance, value: f"{instance.SOME_VALUE}_{value}"
    )


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
        ExampleClass.f3.from_dict(obj, {"add_val": 3})

        assert obj.f1 == "some_object+1"
        assert obj.f2 == "some_object+2"
        assert obj.f3 == "VAL_some_object+3"

    def test_field_from_dict_with_none(self):
        obj = ExampleClass()

        ExampleClass.f1.from_dict(obj, {"another_name": 2})
        ExampleClass.f2.from_dict(obj, {"f1": 1})

        assert obj.f1 == "default"
        assert obj.f2 is None

    def test_field_to_dict_when_no_data(self):
        obj = ExampleClass()
        obj.f1 = None
        assert ExampleClass.f1.to_dict(obj) == {"f1": None}

    def test_field_to_dict_uses_converter(self):
        obj = ExampleClass()
        obj.f1 = 1
        obj.f2 = 2

        assert ExampleClass.f1.to_dict(obj) == {"f1": "some_back+1"}
        assert ExampleClass.f2.to_dict(obj) == {"another_name": "some_back+2"}

    def test_field_default_value(self):
        obj = ExampleClass()

        assert obj.f1 == "default"
        assert obj.f2 is None

        assert ExampleClass.f1.to_dict(obj) == {"f1": "some_back+default"}

    def test_field_read_only(self):
        class ReadOnlyField:
            f1 = DummyField("f1", read_only=True)

        obj = ReadOnlyField()

        with pytest.raises(AttributeError):
            obj.f1 = 1

        ReadOnlyField.f1.from_dict(obj, {"f1": 1})
        assert obj.f1 == "some_object+1"

    def test_field_is_not_exported_to_dict(self):
        class TestClass:
            f1 = DummyField("f1")
            f2 = DummyField("f2", export=False)

        obj = TestClass()
        obj.f1 = 1
        obj.f2 = 2

        assert TestClass.f1.to_dict(obj) == {"f1": "some_back+1"}
        assert TestClass.f2.to_dict(obj) == {}

    def test_field_can_be_cleared_by_delattr(self):
        obj = ExampleClass()
        obj.f1 = 1
        obj.f2 = 2

        assert obj.f1 == 1
        assert obj.f2 == 2

        delattr(obj, "f1")
        delattr(obj, "f2")

        assert obj.f1 == "default"  # return to default value
        assert obj.f2 is None


class TestCommonBehavior:
    field_classes = [
        Attribute,
        Datetime,
        ContentField,
        IsoTime,
        Date,
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
    def test_field_from_dict_when_no_data(self, field_class):
        assert self.from_dict(None, field_class) is None

    @pytest.mark.parametrize("field_class", field_classes)
    def test_field_to_dict_when_no_data(self, field_class):
        assert self.to_dict(None, field_class) is None


class ExampleEnum(Enum):
    a = "aa"
    b = "bb"


class ExampleEnumClass:
    f1 = EnumField("f1", ExampleEnum)


class TestEnumField:
    def test_field_from_dict(self):
        obj = ExampleEnumClass()

        ExampleEnumClass.f1.from_dict(obj, {"f1": "aa"})
        assert obj.f1 == ExampleEnum.a

        ExampleEnumClass.f1.from_dict(obj, {"f1": "bb"})
        assert obj.f1 == ExampleEnum.b

    def test_field_to_dict(self):
        obj = ExampleEnumClass()
        obj.f1 = ExampleEnum.a

        assert ExampleEnumClass.f1.to_dict(obj) == {"f1": "aa"}


class TestContentField:
    class ExampleContentClass:
        f1 = ContentField("f1")

    def test_set_content_from_str(self):
        obj = self.ExampleContentClass()
        obj.f1 = "some content"

        assert obj.f1.value == "some content"

        obj.f1.type = ContentType.TEXT
        obj.f1 = "new content"
        assert obj.f1.value == "new content"
        assert obj.f1.type == ContentType.TEXT

    def test_set_content_from_object(self):
        obj = self.ExampleContentClass()
        obj.f1 = Content("some content")

        assert obj.f1.value == "some content"
        assert str(obj.f1) == "some content"

    def test_set_content_type(self):
        obj = self.ExampleContentClass()
        obj.f1 = Content("some content")
        obj.f1.type = ContentType.TEXT

        assert obj.f1.type == ContentType.TEXT
