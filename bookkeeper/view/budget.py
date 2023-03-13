from typing import Callable

from PySide6 import QtWidgets
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QTableWidgetItem

from bookkeeper.models.budget import Budget, Period
from bookkeeper.view.exceptions.consumption_error import ConsumptionOverflowError
from bookkeeper.view.mapper import Mapper


class BudgetWidget(QtWidgets.QWidget):
    previous_cell_value: str = ''

    def __init__(self,
                 budget_updater: Callable[[Budget], None]):
        super().__init__()

        self.budget_updater = budget_updater

        label = QtWidgets.QLabel("<b>Бюджет</b>")
        self.budget_table = BudgetTable()
        self.budget_table.cellActivated.connect(self.on_cell_activate)
        self.budget_table.cellChanged.connect(self.on_budget_update)
        self.set_consumptions([0, 0, 0])

        widget_layout = QtWidgets.QVBoxLayout()
        widget_layout.addWidget(label)
        widget_layout.addWidget(self.budget_table)
        self.setLayout(widget_layout)

    @Slot()
    def on_budget_update(self) -> None:
        current_item = self.budget_table.currentItem()
        if current_item is None \
                or current_item.column() != 1:
            return

        try:
            new_budget = Mapper.table_item_to_budget(current_item)
            self.budget_updater(new_budget)
        except Exception as ex:
            if current_item.text() != self.previous_cell_value:
                current_item.setText(self.previous_cell_value)
                QtWidgets.QMessageBox.critical(self, "Ошибка", str(ex))

    @Slot()
    def on_cell_activate(self):
        self.previous_cell_value = self.budget_table.currentItem().text()

    def set_consumptions(self, consumptions: list[int]) -> None:
        for_day, for_week, for_month = consumptions[:3]

        day_item = self.budget_table \
            .create_consumption_item(str(for_day))
        week_item = self.budget_table \
            .create_consumption_item(str(for_week))
        month_item = self.budget_table \
            .create_consumption_item(str(for_month))

        self.budget_table.setItem(0, 0, day_item)
        self.budget_table.setItem(1, 0, week_item)
        self.budget_table.setItem(2, 0, month_item)

        try:
            self.check_consumption_overflow(for_day, for_week, for_month)
        except ConsumptionOverflowError as ex:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", str(ex))

    def check_consumption_overflow(self,
                                   for_day: int,
                                   for_week: int,
                                   for_month: int) -> None:
        daily_budget = int(self.budget_table.item(0, 1).text())
        weekly_budget = int(self.budget_table.item(1, 1).text())
        monthly_budget = int(self.budget_table.item(2, 1).text())

        if for_day > daily_budget:
            raise ConsumptionOverflowError(Period.DAY)
        if for_week > weekly_budget:
            raise ConsumptionOverflowError(Period.WEEK)
        if for_month > monthly_budget:
            raise ConsumptionOverflowError(Period.MONTH)


class BudgetTable(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__()
        self.budgets: list[Budget] = []

        self.setColumnCount(2)
        self.setRowCount(3)
        self.setHorizontalHeaderLabels(["Потрачено", "Бюджет"])
        self.setVerticalHeaderLabels(["День", "Неделя", "Месяц"])
        self.stretch_table_elements()

    def stretch_table_elements(self) -> None:
        for h in [self.horizontalHeader(), self.verticalHeader()]:
            h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def set_budgets(self, budgets: list[Budget]) -> None:
        self.budgets = budgets[:3]
        for_day = budgets[0]
        for_week = budgets[1]
        for_month = budgets[2]

        self.setItem(0, 1, QTableWidgetItem(
            str(for_day.total_amount) if for_day else ''))
        self.setItem(1, 1, QTableWidgetItem(
            str(for_week.total_amount) if for_week else ''))
        self.setItem(2, 1, QTableWidgetItem(
            str(for_month.total_amount) if for_month else ''))

    def set_expenses(self, expenses: list[int]) -> None:
        for_day, for_week, for_month = expenses[:3]

        day_item = self.create_consumption_item(str(for_day))
        week_item = self.create_consumption_item(str(for_week))
        month_item = self.create_consumption_item(str(for_month))

        self.setItem(0, 0, day_item)
        self.setItem(1, 0, week_item)
        self.setItem(2, 0, month_item)

    @staticmethod
    def create_consumption_item(consumption: str) -> QTableWidgetItem:
        item = QTableWidgetItem(consumption)
        item.setFlags(~Qt.ItemIsEnabled)
        return item
