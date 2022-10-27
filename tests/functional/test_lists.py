from .utils import run_functional_condition

pytestmark = run_functional_condition


def test_a_test(client):
    assert client
