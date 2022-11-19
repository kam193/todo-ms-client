from todoms.convertable import BaseConvertableFieldsObject
from todoms.fields.basic import Attribute, Content


class SimpleObject(BaseConvertableFieldsObject):
    name = Attribute("name")
    other = Attribute("other")


class ComplexObject(BaseConvertableFieldsObject):
    new = Attribute("old")


class ComplexObjectWithConverting(BaseConvertableFieldsObject):
    new = Content("old")


class TestBaseConvertableFieldsObject:
    def test_convertable_object_creates_obj_from_data(self):
        obj = SimpleObject.from_dict(
            {"name": "name-1", "other": "val-1", "not_attr": "ignore"}
        )

        assert obj.name == "name-1"
        assert obj.other == "val-1"
        assert getattr(obj, "not_attr", None) is None

    def test_convertable_object_create_translates_attributes(self):
        obj_1 = ComplexObject.from_dict({"old": "data"})

        assert obj_1.new == "data"

    def test_convertable_object_create_converts_attributes_format(self):
        obj_1 = ComplexObjectWithConverting.from_dict({"old": {"content": "converted"}})

        assert obj_1.new == "converted"

    def test_convertable_object_from_dict_pass_additional_arguments(self):
        obj = SimpleObject.from_dict({"name": "name-1"}, other="passed-implicit")

        assert obj.name == "name-1"
        assert obj.other == "passed-implicit"

    def test_convertable_object_simple_to_dict(self):
        convertable = SimpleObject.from_dict({"name": "name-1", "other": "val-1"})

        data_dict = convertable.to_dict()

        assert data_dict == {"name": "name-1", "other": "val-1"}

    def test_convertable_object_complex_to_dict(self):
        obj = ComplexObject(new="data")

        data_dict = obj.to_dict()

        assert data_dict == {"old": "data"}

    def test_convertable_object_complex_to_dict_with_converter(self):
        obj = ComplexObjectWithConverting(new="data")

        data_dict = obj.to_dict()

        assert data_dict == {"old": {"content": "data", "contentType": "html"}}
