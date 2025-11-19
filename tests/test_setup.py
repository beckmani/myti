"""Basic test to verify the test infrastructure is working."""

import pytest
from hypothesis import given, strategies as st


def test_basic():
    """Verify basic test execution works."""
    assert True


@given(st.text())
def test_hypothesis_works(text):
    """Verify Hypothesis property-based testing works."""
    assert isinstance(text, str)
