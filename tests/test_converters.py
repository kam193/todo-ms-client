from unittest.mock import Mock
from todoms.converters import AttributeConverter


def test_default_converter_returns_input():
    attr_converter = AttributeConverter("original", "new name")
    data = Mock()

    assert attr_converter.obj_converter(data) == data
