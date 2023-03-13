import sqlite3
from dataclasses import dataclass
from datetime import datetime

import pytest

from bookkeeper.repository.sqlite_repository import SQLiteRepository

DB_FILE = "resources/test_database.db"


@pytest.fixture
def create_bd():
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS custom")
        cursor.execute("CREATE TABLE custom(field_1, field_2)")
    connection.close()


@pytest.fixture
def custom_class():
    @dataclass
    class Custom:
        pk: int = 0
        field_1: int = 0
        field_2: str = "Test_value"

    return Custom


@pytest.fixture
def repo(custom_class, create_bd):
    return SQLiteRepository(db_file=DB_FILE, clazz=custom_class)


def test_resolve_type(repo):
    assert repo._resolve_type(type('abc')) == 'TEXT'
    assert repo._resolve_type(type(1)) == 'INTEGER'
    assert repo._resolve_type(type(1.23)) == 'REAL'
    assert repo._resolve_type(type([])) == 'TEXT'
    assert repo._resolve_type(type(datetime.now())) == 'TIMESTAMP'
    assert repo._resolve_type(type(int | None)) == 'TEXT'


def test_condition_adding(repo):
    test_query = "SELECT * FROM table_name"
    conditions = {"A": 1}
    received_query = repo._add_conditions_to_query(test_query, conditions)
    test_query = test_query + " WHERE A = ?"
    assert test_query == received_query


def test_crud(repo, custom_class):
    # add method test
    custom = custom_class(field_1=1, field_2="test_crud")
    pk = repo.add(custom)
    assert pk == custom.pk
    # get method test
    received_custom = repo.get(pk)
    assert received_custom is not None
    assert received_custom.pk == custom.pk
    assert received_custom.field_1 == custom.field_1
    assert received_custom.field_2 == custom.field_2
    # update method test
    updated_custom = custom_class(field_1=11, field_2="test_crud_upd", pk=pk)
    repo.update(updated_custom)
    received_custom = repo.get(pk)
    assert received_custom == updated_custom
    # delete method test
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class(field_1=1, pk=1)
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_update_not_existing(repo, custom_class):
    obj = custom_class(field_1=1, pk=100)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class(field_1=1, pk=0)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_cannot_get_not_existing(repo):
    assert repo.get(-1) is None


def test_cannot_delete_not_existing(repo):
    with pytest.raises(ValueError):
        repo.delete(-1)


def test_get_all(repo, custom_class):
    objs = [custom_class(field_1=i) for i in range(5)]
    for obj in objs:
        repo.add(obj)

    objs_get_all = repo.get_all()
    assert objs == objs_get_all


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class(field_1=1)
        o.field_1 = i
        o.field_2 = 'test'
        repo.add(o)
        objects.append(o)
    assert [objects[0]] == repo.get_all({'field_1': 0})
    assert objects == repo.get_all({'field_2': 'test'})
