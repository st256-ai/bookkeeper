from typing import Callable

from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow

from bookkeeper.models.budget import Budget, Period
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.view.budget import BudgetWidget
from bookkeeper.view.category import CategoryWidget
from bookkeeper.view.expense import ExpenseWidget


class MainWindow(QMainWindow):

    def __init__(self,
                 category_creator: Callable[[Category], int],
                 category_deleter: Callable[[int], None],
                 budget_updater: Callable[[Budget], None],
                 expense_getter: Callable[[int], Expense],
                 expense_creator: Callable[[Expense], int],
                 expense_updater: Callable[[Expense], None],
                 expense_deleter: Callable[[Expense], None]):
        super().__init__()
        self.category_creator = category_creator
        self.category_deleter = category_deleter
        self.budget_updater = budget_updater
        self.expense_getter = expense_getter
        self.expense_creator = expense_creator
        self.expense_updater = expense_updater
        self.expense_deleter = expense_deleter

        self.expense_widget = ExpenseWidget(self.expense_creator,
                                            self.expense_updater,
                                            self.expense_deleter,
                                            self.expense_getter)
        self.budget_widget = BudgetWidget(self.budget_updater)
        self.category_widget = CategoryWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.expense_widget)
        layout.addWidget(self.budget_widget)
        layout.addWidget(self.category_widget)

        box = QtWidgets.QGroupBox()
        box.setLayout(layout)
        self.setCentralWidget(box)

    # TODO IMPLEMENT
    def create_category(self, category: Category) -> None:
        pass

    # TODO IMPLEMENT
    def set_category_list(self, categories: list[Category]) -> None:
        pass

    def set_budget_list(self, budgets: list[Budget]) -> None:
        d_budget, w_budget, m_budget = [0, 0, 0]
        d_expense, w_expense, m_expense = [0, 0, 0]

        for bud in budgets:
            if bud.period == Period.DAY.name:
                d_budget = bud.total_amount
                d_expense = bud.consumed_amount
            if bud.period == Period.WEEK.name:
                w_budget = bud.total_amount
                w_expense = bud.consumed_amount
            if bud.period == Period.MONTH.name:
                m_budget = bud.total_amount
                m_expense = bud.consumed_amount
        self.budget_widget.set_budgets([d_budget, w_budget, m_budget])
        self.budget_widget.set_consumptions([d_expense, w_expense, m_expense])

    def set_expense_list(self, expenses: list[Expense]) -> None:
        pass

    def update_consumptions(self, consumptions: list[int]) -> None:
        self.budget_widget.set_consumptions(
            [consumptions[0], consumptions[1], consumptions[2]])
