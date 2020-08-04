from todoms.convertable import BaseConvertableObject
from todoms.converters.basic import AttributeConverter, ContentAttrConverter


class SimpleObject(BaseConvertableObject):
    ATTRIBUTES = ("name", "other")

    def __init__(self, name, other):
        self.name = name
        self.other = other


class ComplexObject(BaseConvertableObject):
    ATTRIBUTES = (AttributeConverter("old", "new"),)

    def __init__(self, new):
        self.new = new


class ComplexObjectWithConverting(BaseConvertableObject):
    ATTRIBUTES = (ContentAttrConverter("old", "new"),)

    def __init__(self, new):
        self.new = new


class TestBaseConvertableObject:
    def test_convertable_object_creates_obj_from_data(self):
        obj = SimpleObject.create_from_dict(
            {"name": "name-1", "other": "val-1", "not_attr": "ignore"}
        )

        assert obj.name == "name-1"
        assert obj.other == "val-1"
        assert getattr(obj, "not_attr", None) is None

    def test_convertable_object_create_translates_attributes(self):
        obj_1 = ComplexObject.create_from_dict({"old": "data"})

        assert obj_1.new == "data"

    def test_convertable_object_create_converts_attributes_format(self):
        obj_1 = ComplexObjectWithConverting.create_from_dict(
            {"old": {"content": "converted"}}
        )

        assert obj_1.new == "converted"

    def test_convertable_object_from_dict_pass_additional_arguments(self):
        obj = SimpleObject.create_from_dict({"name": "name-1"}, other="passed-implicit")

        assert obj.name == "name-1"
        assert obj.other == "passed-implicit"

    def test_convertable_object_simple_to_dict(self):
        convertable = SimpleObject.create_from_dict(
            {"name": "name-1", "other": "val-1"}
        )

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
