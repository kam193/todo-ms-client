from todoms.converters.field import Field


class ExampleClass:
    f1 = Field("f1")
    f2 = Field("another_name")


def test_crud_field():
    obj = ExampleClass()
    obj.f1 = 1

    assert obj.f1 == 1
    assert obj.f2 is None

    obj.f1 = 2
    assert obj.f1 == 2


def test_field_from_dict():
    obj = ExampleClass()

    ExampleClass.f1.from_dict(obj, {"f1": 1, "another_name": 2})
    ExampleClass.f2.from_dict(obj, {"f1": 1, "another_name": 2})

    assert obj.f1 == 1
    assert obj.f2 == 2


def test_field_from_dict_with_none():
    obj = ExampleClass()

    ExampleClass.f1.from_dict(obj, {"another_name": 2})
    ExampleClass.f2.from_dict(obj, {"f1": 1})

    assert obj.f1 is None
    assert obj.f2 is None


def test_field_to_dict():
    obj = ExampleClass()
    obj.f1 = 1
    obj.f2 = 2

    assert ExampleClass.f1.to_dict(obj) == {"f1": 1}
    assert ExampleClass.f2.to_dict(obj) == {"another_name": 2}
