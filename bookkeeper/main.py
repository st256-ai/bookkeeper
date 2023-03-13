"""
Main файл приложения
"""

import os
from datetime import datetime, timedelta

from bookkeeper.models.budget import Budget
from bookkeeper.models.budget import Period
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree, INIT_CATEGORIES, DB_PATH
from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.view.view import View


class Bookkeeper:
    """
    Presenter с графическим интерфейсом
    """

    DAY = 1
    WEEK = 7
    MONTH = 30

    def __init__(self, view: AbstractView,
                 category_repo: AbstractRepository[Category],
                 expense_repo: AbstractRepository[Expense],
                 budget_repo: AbstractRepository[Budget]) -> None:
        self.view = view
        self.category_repo = category_repo
        self.expense_repo = expense_repo
        self.budget_repo = budget_repo

        self.view.register_expense_updater(self.update_expense)
        self.view.register_expense_deleter(self.delete_expense)
        self.view.register_expense_creator(self.create_expense)
        self.view.register_expense_getter(self.expense_repo.get)

        self.view.register_category_deleter(self.delete_category)
        self.view.register_category_creator(self.create_category)

        self.view.register_budget_updater(self.update_budget)

    def init_db(self) -> None:
        """
        Вставка некоторых значений по-умолчанию
        """
        Category.create_from_tree(read_tree(INIT_CATEGORIES), self.category_repo)
        self.expense_repo.add(Expense(120, 1, comment='Some comment 1'))
        self.expense_repo.add(Expense(900, 7, comment='Some comment 2'))
        self.budget_repo.add(Budget(1000, 100, Period.DAY))
        self.budget_repo.add(Budget(7000, 200, Period.WEEK))
        self.budget_repo.add(Budget(30000, 300, Period.MONTH))

    def run(self) -> None:
        # self.view.set_category_list(self.category_repo.get_all())
        self.view.set_expense_list(self.expense_repo.get_all())
        self.view.set_budget_list(self.budget_repo.get_all())
        self.view.run()

    def update_expense(self, expense: Expense) -> None:
        self.expense_repo.update(expense)
        consumptions = self.recalculate_consumptions(expense)
        self.view.update_consumptions(consumptions)

    def delete_expense(self, expense: Expense) -> None:
        self.expense_repo.delete(expense.pk)
        expense.amount = -expense.amount
        consumptions = self.recalculate_consumptions(expense)
        self.view.update_consumptions(consumptions)

    def create_expense(self, expense: Expense) -> int:
        pk = self.expense_repo.add(expense)
        consumptions = self.recalculate_consumptions(expense)
        self.view.update_consumptions(consumptions)
        return pk

    def delete_category(self, pk: int) -> None:
        self.category_repo.delete(pk)
        self.view.set_category_list(self.category_repo.get_all())

    def create_category(self, category: Category) -> int:
        pk = self.category_repo.add(category)
        self.view.set_category_list(self.category_repo.get_all())
        return pk

    def update_budget(self, budget: Budget) -> None:
        old_budgets = self.budget_repo.get_all()
        for bud in old_budgets:
            if bud.pk == budget.pk:
                bud.total_amount = budget.total_amount
                self.budget_repo.update(bud)
                return
        self.budget_repo.add(budget)

    def recalculate_consumptions(self, expense: Expense):
        day_con, week_con, month_con = 0, 0, 0
        today = datetime.now()
        if expense.expense_date >= today - timedelta(days=self.DAY):
            day_con += expense.amount
        if expense.expense_date >= today - timedelta(days=self.WEEK):
            week_con += expense.amount
        if expense.expense_date >= today - timedelta(days=self.MONTH):
            month_con += expense.amount
        return [day_con, week_con, month_con]


db_init_needed = not os.path.isfile(DB_PATH)

app_view: AbstractView = View()
cat_repo = SQLiteRepository[Category](DB_PATH, Category)
exp_repo = SQLiteRepository[Expense](DB_PATH, Expense)
bud_repo = SQLiteRepository[Budget](DB_PATH, Budget)

b = Bookkeeper(app_view, cat_repo, exp_repo, bud_repo)
if db_init_needed:
    b.init_db()

b.run()
