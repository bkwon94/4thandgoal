"""
Reads the shard of a pytest run from the env value PYTEST_SHARD, such as "2/2", and picks the tests of that shard.
CI runs the parallel pipeline tests in a matrix of shards, so each job runs only its own part of the tests.
"""
import re

import pytest

ENV = "PYTEST_SHARD"


def shard_of_env(value: str | None) -> tuple[int, int] | None:
    """The shard as (current, total), or None when the value is not set, so a local run takes every test. A value that
    names no shard stops the run, because a bad value would make each job of the matrix run every test."""
    if value is None or value == "":
        return None
    match = re.fullmatch(r"(\d+)/(\d+)", value)
    current, total = (int(match[1]), int(match[2])) if match else (0, 0)
    if not 1 <= current <= total:
        raise pytest.UsageError(f'{ENV} must be <current>/<total>, with 1 <= current <= total, not "{value}".')
    return current, total


def in_shard(node_ids: list[str], shard: tuple[int, int]) -> set[str]:
    """The node ids of `shard`. The ids sort by name, and the shard keeps each Nth id of that order. The order does not
    depend on the order of collection, so each worker of xdist and each job picks the same split. Every id lands in
    exactly one shard, and the tests of one slow file spread over the shards."""
    current, total = shard
    return {node_id for rank, node_id in enumerate(sorted(node_ids)) if rank % total == current - 1}
