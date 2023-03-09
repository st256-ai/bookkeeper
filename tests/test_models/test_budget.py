import pytest

from bookkeeper.models.budget import Period, Budget
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_entity():
    b = Budget(1000, 10, Period.DAY, 1)
    assert b.total_amount == 1000
    assert b.category_id == 10
    assert b.period == Period.DAY
    assert b.pk == 1


def test_can_add_to_repo(repo):
    b = Budget(1000, 10, Period.DAY)
    pk = repo.add(b)
    assert b.pk == pk


def test_can_add_with_hour_period(repo):
    b = Budget(1000, 10, Period.HOUR)
    pk = repo.add(b)
    assert b.pk == pk
