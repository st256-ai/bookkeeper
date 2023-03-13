"""
Вспомогательные функции
"""
import sqlite3
from typing import Iterable, Iterator

from bookkeeper.models.budget import Budget, Period
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository

DB_PATH = '../resources/database.db'

INIT_CATEGORIES = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _lines_with_indent(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    for line in lines:
        if not line or line.isspace():
            continue
        yield _get_indent(line), line.strip()


def read_tree(lines: Iterable[str]) -> list[tuple[str, str | None]]:
    """
    Прочитать структуру дерева из текста на основе отступов. Вернуть список
    пар "потомок-родитель" в порядке топологической сортировки. Родитель
    элемента верхнего уровня - None.

    Пример. Следующий текст:
    parent
        child1
            child2
        child3

    даст такое дерево:
    [('parent', None), ('child1', 'parent'),
     ('child2', 'child1'), ('child3', 'parent')]

    Пустые строки игнорируются.

    Parameters
    ----------
    lines - Итерируемый объект, содержащий строки текста (файл или список строк)

    Returns
    -------
    Список пар "потомок-родитель"
    """
    parents: list[tuple[str | None, int]] = []
    last_indent = -1
    last_name = None
    result: list[tuple[str, str | None]] = []
    for i, (indent, name) in enumerate(_lines_with_indent(lines)):
        if indent > last_indent:
            parents.append((last_name, last_indent))
        elif indent < last_indent:
            while indent < last_indent:
                _, last_indent = parents.pop()
            if indent != last_indent:
                raise IndentationError(
                    f'unindent does not match any outer indentation '
                    f'level in line {i}:\n'
                )
        result.append((name, parents[-1][0]))
        last_name = name
        last_indent = indent
    return result


create_category_query = "CREATE TABLE IF NOT EXISTS category (" + \
                        "pk INTEGER PRIMARY KEY AUTOINCREMENT," + \
                        "name TEXT UNIQUE NOT NULL CHECK(length(name) < 20)," + \
                        "parent INTEGER," + \
                        "FOREIGN KEY (parent) REFERENCES category (pk) ON DELETE SET NULL);"

create_expense_query = "CREATE TABLE IF NOT EXISTS expense (" + \
                       "pk INTEGER PRIMARY KEY AUTOINCREMENT," + \
                       "amount INTEGER NOT NULL CHECK(amount >= 0.0)," + \
                       "category INTEGER," + \
                       "expense_date TIMESTAMP NOT NULL," + \
                       "added_date TIMESTAMP NOT NULL," + \
                       "comment TEXT CHECK(length(comment) <= 20)," + \
                       "FOREIGN KEY (category) REFERENCES category (pk) ON DELETE SET NULL);"

create_budget_query = "CREATE TABLE IF NOT EXISTS budget (" + \
                      "pk INTEGER PRIMARY KEY AUTOINCREMENT," + \
                      "total_amount INTEGER NOT NULL CHECK(total_amount >= 0.0)," + \
                      "consumed_amount INTEGER NOT NULL CHECK(consumed_amount >= 0.0)," + \
                      "period TEXT NOT NULL DEFAULT 'День' CHECK(period IN ('DAY', 'WEEK', 'MONTH')));"

drop_category_query = "DROP TABLE IF EXISTS category;"
drop_expense_query = "DROP TABLE IF EXISTS expense;"
drop_budget_query = "DROP TABLE IF EXISTS budget;"


def create_tables():
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(create_budget_query)
        cursor.execute(create_expense_query)
        cursor.execute(create_category_query)
    connection.close()


def drop_tables():
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(drop_budget_query)
        cursor.execute(drop_expense_query)
        cursor.execute(drop_category_query)
    connection.close()


def init_db_if_needed(category_repo: AbstractRepository[Category],
                      expense_repo: AbstractRepository[Expense],
                      budget_repo: AbstractRepository[Budget]) -> None:
    """
    Вставка некоторых значений по-умолчанию
    """
    drop_tables()
    create_tables()
    expenses = expense_repo.get_all()
    if len(expenses) > 0:
        return

    Category.create_from_tree(read_tree(INIT_CATEGORIES), category_repo)

    budget_repo.add(Budget(1000, 0, Period.DAY.name, 0))
    budget_repo.add(Budget(7000, 0, Period.WEEK.name, 0))
    budget_repo.add(Budget(30000, 0, Period.MONTH.name, 0))
    print()
