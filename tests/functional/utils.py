from os import getenv

import pytest

run_functional_condition = pytest.mark.skipif(
    getenv("RUN_FUNCTIONAL_TESTS", "0") != "1", reason="RUN_FUNCTIONAL_TESTS not set"
)
