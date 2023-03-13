from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


class Validator:

    def __init__(self):
        pass

    @staticmethod
    def validate_budget(budget: Budget) -> None:
        if budget is None:
            raise ValueError("Пожалуйста, задайте новое значение бюджета")
        if budget.total_amount < 0:
            raise ValueError("Бюджет не может быть отрицательным")

    @staticmethod
    def validate_category(category: Category) -> None:
        pass

    @staticmethod
    def validate_expense(expense: Expense) -> None:
        pass
