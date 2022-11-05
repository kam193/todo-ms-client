# TODO: Type hints


class Field:
    def __init__(self, dict_name: str):
        self.dict_name = dict_name

    def __set_name__(self, _, name):
        self.name = name

    def __get__(self, instance, _=None):
        if not instance:
            return self
        return self._get_value(instance)

    def __set__(self, instance, value):
        self._set_value(instance, value)

    def from_dict(self, instance, data: dict):
        if self.dict_name not in data:
            return
        self._set_value(instance, self.convert_from_dict(data))

    def to_dict(self, instance) -> dict:
        return {self.dict_name: self.convert_for_dict(instance)}

    def convert_from_dict(self, data: dict):
        return data.get(self.dict_name)

    def convert_for_dict(self, instance):
        return self._get_value(instance)

    def _get_value(self, instance):
        return instance.__dict__.get(self.name)

    def _set_value(self, instance, value):
        instance.__dict__[self.name] = value
