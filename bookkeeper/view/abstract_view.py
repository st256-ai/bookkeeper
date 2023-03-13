from typing import Protocol, Callable

from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


class AbstractView(Protocol):
    def run(self) -> None:
        pass

    def set_category_list(self, categories: list[Category]) -> None:
        pass

    def set_budget_list(self, categories: list[Budget]) -> None:
        pass

    def update_consumptions(self, consumptions: list[int]) -> None:
        pass

    def set_expense_list(self, categories: list[Expense]) -> None:
        pass
