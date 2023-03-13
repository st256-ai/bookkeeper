from typing import Callable

from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QMainWindow

from bookkeeper.models.budget import Budget, Period
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.view.budget import BudgetWidget
from bookkeeper.view.category import CategoryWidget
from bookkeeper.view.expense import ExpenseWidget


class MainWindow(QMainWindow):
    BOOKKEEPER_APP_LOGO_PATH: str = "../../resources/logo.png"

    category_id_name_mapping: dict[int, str] = dict()
    category_name_id_mapping: dict[str, int] = dict()
    categories: list[Category] = []
    budgets: list[Budget] = []
    expenses: list[Expense] = []
    category_creator: Callable[[Category], int] = lambda x: -1
    category_deleter: Callable[[int], None] = lambda x: None
    budget_updater: Callable[[Budget], None] = lambda x: None
    expense_getter: Callable[[int], Expense] = lambda x: Expense
    expense_creator: Callable[[Expense], int] = lambda x: -1
    expense_updater: Callable[[Expense], None] = lambda x: None
    expense_deleter: Callable[[Expense], None] = lambda x: None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bookkeeper")
        window_icon = QtGui.QIcon()
        window_icon.addFile(self.BOOKKEEPER_APP_LOGO_PATH)
        self.setWindowIcon(window_icon)

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
        print('create_category')
        self.category_creator(category)

    # TODO IMPLEMENT
    def set_category_list(self, categories: list[Category]) -> None:
        self.categories = categories
        self.category_id_name_mapping = {c.pk: c.name for c in categories}
        self.category_name_id_mapping = {c.name: c.pk for c in categories}

    # TODO IMPLEMENT
    def set_budget_list(self, budgets: list[Budget]) -> None:
        self.budgets = budgets
        for_day = self.get_bud_by_cat_and_dur(budgets, None, Period.DAY)
        for_week = self.get_bud_by_cat_and_dur(budgets, None, Period.WEEK)
        for_month = self.get_bud_by_cat_and_dur(budgets, None, Period.MONTH)
        self.budget_widget.budget_table.set_budgets([for_day, for_week, for_month])

    def set_expense_list(self, expenses: list[Expense]) -> None:
        self.expenses = expenses
        self.expense_widget.expense_table.set_data(expenses, self.category_id_name_mapping)
        self.update_budgets_with_expense_update(expenses)

    def update_consumptions(self, consumptions: list[int]) -> None:
        self.budget_widget.set_consumptions(
            [consumptions[0], consumptions[1], consumptions[2]])
