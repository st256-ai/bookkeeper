import sys
from typing import Callable
from PySide6 import QtWidgets, QtGui

from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.view.main_window import MainWindow


class View(AbstractView):
    BOOKKEEPER_APP_LOGO_PATH: str = "../../resources/logo.png"

    def __init__(self,
                 category_creator: Callable[[Category], int],
                 category_deleter: Callable[[int], None],
                 budget_updater: Callable[[Budget], None],
                 expense_getter: Callable[[int], Expense],
                 expense_creator: Callable[[Expense], int],
                 expense_updater: Callable[[Expense], None],
                 expense_deleter: Callable[[Expense], None]) -> None:
        super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)

        self.window = MainWindow(
            category_creator, category_deleter, budget_updater,
            expense_getter, expense_creator, expense_updater,
            expense_deleter
        )

    def run(self) -> None:
        window_icon = QtGui.QIcon()
        window_icon.addFile(self.BOOKKEEPER_APP_LOGO_PATH)
        self.window.setWindowIcon(window_icon)
        self.window.setWindowTitle("Bookkeeper")

        self.window.show()
        sys.exit(self.app.exec())

    def set_category_list(self, categories: list[Category]) -> None:
        self.window.set_category_list(categories)

    def set_budget_list(self, budgets: list[Budget]) -> None:
        self.window.set_budget_list(budgets)

    def set_expense_list(self, expenses: list[Expense]) -> None:
        self.window.set_expense_list(expenses)

    def update_consumptions(self, consumptions: list[int]) -> None:
        self.window.update_consumptions(consumptions)
