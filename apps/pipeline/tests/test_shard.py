"""
Tests of the shard of a pytest run, read from the env value PYTEST_SHARD.
CI runs the parallel pipeline tests in a matrix of shards, and each test must run in exactly one shard.
"""
import pytest
from shard import in_shard, shard_of_env


def test_no_value_means_no_shard_so_a_local_run_takes_every_test():
    assert shard_of_env(None) is None
    assert shard_of_env("") is None


def test_reads_2_of_3_as_the_second_of_three_shards():
    assert shard_of_env("2/3") == (2, 3)


@pytest.mark.parametrize("bad", ["2", "0/2", "3/2", "a/b", "1/2/1", " 1/2"])
def test_stops_on_a_value_that_names_no_shard(bad):
    with pytest.raises(pytest.UsageError, match="PYTEST_SHARD"):
        shard_of_env(bad)


def test_each_id_lands_in_exactly_one_shard_whatever_the_order():
    ids = [f"tests/test_{name}.py::test_{n}" for name in "cab" for n in range(7)]
    for total in (1, 2, 3):
        shards = [in_shard(ids, (current, total)) for current in range(1, total + 1)]
        assert set().union(*shards) == set(ids)
        assert sum(len(each) for each in shards) == len(ids)
        assert shards == [in_shard(list(reversed(ids)), (current, total)) for current in range(1, total + 1)]


def test_the_tests_of_one_file_spread_over_the_shards():
    ids = [f"tests/test_slow.py::test_{n:02d}" for n in range(10)]
    assert [len(in_shard(ids, (current, 2))) for current in (1, 2)] == [5, 5]
