"""
Main файл приложения
"""

from datetime import datetime, timedelta

from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import DB_PATH
from bookkeeper.view.view import View


class Bookkeeper:
    """
    Presenter с графическим интерфейсом
    """

    DAY = 1
    WEEK = 7
    MONTH = 30

    def __init__(self,
                 category_repo: AbstractRepository[Category],
                 expense_repo: AbstractRepository[Expense],
                 budget_repo: AbstractRepository[Budget]) -> None:

        self.category_repo = category_repo
        self.expense_repo = expense_repo
        self.budget_repo = budget_repo

        self.view = View(
            self.create_category,
            self.delete_category,
            self.update_budget,
            self.expense_repo.get,
            self.create_expense,
            self.update_expense,
            self.delete_expense
        )

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


cat_repo = SQLiteRepository[Category](DB_PATH, Category)
exp_repo = SQLiteRepository[Expense](DB_PATH, Expense)
bud_repo = SQLiteRepository[Budget](DB_PATH, Budget)
# init_db_if_needed(cat_repo, exp_repo, bud_repo)

b = Bookkeeper(cat_repo, exp_repo, bud_repo)
b.run()
