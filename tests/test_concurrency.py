"""
Unit tests for the `concurrency` module.

"""
from __future__ import annotations

import pytest
from prefect import flow, task

from prefecto.concurrency import BatchTask


@task
def add(a, b):
    """Add two numbers."""
    return a + b


class TestBatchTask:
    """Unit tests for `BatchTask`."""

    def test_make_batches(self):
        """Test `_make_batches`."""
        batches = BatchTask(add, 3)._make_batches(a=[1, 2, 3, 4, 5], b=[2, 3, 4, 5, 6])
        assert batches == [{"a": [1, 2, 3], "b": [2, 3, 4]}, {"a": [4, 5], "b": [5, 6]}]

    @pytest.mark.parametrize(
        "a,b,expectation",
        [
            ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6], [3, 5, 7, 9, 11]),
            ([1, 2], [2, 3], [3, 5]),
            ([], [], []),
        ],
    )
    def test_map(self, a: list[int], b: list[int], expectation: list[int], harness):
        """Test `BatchTask.map`."""

        @task
        def realize(futures: list[int]):
            """Converts futures to their values."""
            return futures

        @flow
        def test() -> list[int]:
            """Test flow."""
            futures = BatchTask(add, 3).map(a, b)
            return realize(futures)

        result = test()
        assert result == expectation
