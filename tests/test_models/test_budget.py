import pytest

from bookkeeper.models.budget import Budget
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_entity():
    b = Budget(1, 10, 1000, 1)
    assert b.duration == 1
    assert b.category == 10
    assert b.amount == 1000
    assert b.pk == 1


def test_create_entity_without_category():
    b = Budget(1, None, 1000, 1)
    assert b.duration == 1
    assert b.category is None
    assert b.amount == 1000
    assert b.pk == 1


def test_can_add_to_repo(repo):
    b = Budget(1, 10, 1000)
    pk = repo.add(b)
    assert b.pk == pk
