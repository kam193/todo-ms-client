from todoms.recurrence import Recurrence


class TestRecurrence:
    def test_recurrence_to_dict(self):
        class ToDict1:
            def to_dict(self):
                return "dict1"

        class ToDict2:
            def to_dict(self):
                return "dict2"

        recurrence = Recurrence(ToDict1(), ToDict2())
        assert recurrence.to_dict() == {"pattern": "dict1", "range": "dict2"}
