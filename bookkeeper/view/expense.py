import datetime
from typing import Callable, Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QFormLayout, QTableWidgetItem, QLineEdit, QComboBox
from bookkeeper.models.expense import Expense
from bookkeeper.view.exceptions.validation_error import ValidationError


class ExpenseWidget(QtWidgets.QWidget):
    previous_cell_value: str = ''

    attributes_to_columns = \
        {0: 'expense_date', 1: 'amount', 2: 'category', 3: 'comment'}

    def __init__(self,
                 expense_creator: Callable[[Expense], int],
                 expense_updater: Callable[[Expense], None],
                 expense_deleter: Callable[[Expense], None],
                 expense_getter: Callable[[int], Expense]):
        super().__init__()

        self.expense_creator = expense_creator
        self.expense_updater = expense_updater
        self.expense_deleter = expense_deleter
        self.expense_getter = expense_getter

        layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()

        self.expense_table = ExpenseTable()
        self.expense_table.cellClicked.connect(self.cell_clicked)
        self.expense_table.cellChanged.connect(self.cell_changed)

        label = QtWidgets.QLabel("<b>Последние Расходы</b>")
        add_button = QtWidgets.QPushButton("Добавить")
        add_button.clicked.connect(self.arise_add_dialog_form)

        self.delete_button = QtWidgets.QPushButton("Удалить")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_expense_table_row)

        button_layout.addWidget(add_button)
        button_layout.addWidget(self.delete_button)

        layout.addWidget(label)
        layout.addWidget(self.expense_table)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    @Slot()
    def cell_clicked(self) -> None:
        self.previous_cell_value = self.expense_table.currentItem().text()
        self.delete_button.setEnabled(True)

    @Slot()
    def cell_changed(self) -> None:
        self.delete_button.setEnabled(False)
        current_item = self.expense_table.currentItem()
        pk = current_item.row()
        column = current_item.column()
        attr = self.attributes_to_columns.get(column)

        try:
            expense = self.expense_getter(pk)
            expense.modify_attr(attr, current_item.text())
            self.expense_updater(expense)
        except Exception as ex:
            if current_item.text() != self.previous_cell_value:
                current_item.setText(self.previous_cell_value)
                QtWidgets.QMessageBox.critical(self, "Ошибка", str(ex))

    @Slot()
    def delete_expense_table_row(self):
        row = self.expense_table.currentRow()
        self.expense_table.delete_row(row)
        self.delete_button.setEnabled(False)

        try:
            expense = self.expense_getter(row)
            self.expense_deleter(expense)
        except Exception as ex:
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(ex))

    @Slot()
    def arise_add_dialog_form(self):
        add_form = AddDialogForm()
        add_form.exec()
        if add_form.is_ok_clicked:
            values_dict = add_form.get_data_from_forms()
            self.validate_values(values_dict)
            self.expense_table.add_new_row(values_dict)
            add_form.is_ok_clicked = False

            try:
                expense = self.map_to_expense(values_dict)
                self.expense_creator(expense)
            except Exception as ex:
                QtWidgets.QMessageBox.critical(self, "Ошибка", str(ex))

    @staticmethod
    def map_to_expense(values_dict: dict[Any]) -> Expense:
        expense = Expense()
        for (key, value) in values_dict:
            expense.modify_attr(key, value)
        expense.added_date = datetime.datetime.now()

    @staticmethod
    def validate_values(values_dict: dict[Any]) -> None:
        mandatory_params = values_dict
        mandatory_params.pop("comment")
        for (key, value) in mandatory_params:
            if value is None:
                raise ValidationError(key)


class ExpenseTable(QtWidgets.QTableWidget):

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Дата", "Сумма", "Категория", "Комментарий"])
        self.stretch_table_elements()

    def stretch_table_elements(self) -> None:
        for h in [self.horizontalHeader()]:
            h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def add_new_row(self,
                    value_dict: dict) -> None:
        next_row = self.rowCount()
        self.insertRow(next_row)

        date = value_dict.get("expense_date")
        amount = value_dict.get("amount")
        category_id = value_dict.get("category")
        comment = value_dict.get("comment")

        self.setItem(next_row, 0, QTableWidgetItem(date))
        self.setItem(next_row, 1, QTableWidgetItem(f"{amount}"))
        self.setItem(next_row, 2, QTableWidgetItem(f"{category_id}"))
        self.setItem(next_row, 3, QTableWidgetItem(comment))

    def delete_row(self, row: int) -> None:
        self.removeRow(row)


class DateWidget(QtWidgets.QDateEdit):
    def __init__(self, date: QtCore.QDate = QtCore.QDate.currentDate()) -> None:
        super().__init__(date)
        self.setCalendarPopup(True)
        self.setDisplayFormat('dd.MM.yyyy')
        calendar = self.calendarWidget()
        calendar.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Monday)
        calendar.setGridVisible(True)


class AddDialogForm(QtWidgets.QDialog):
    is_ok_clicked: bool = False

    date_input: DateWidget
    amount_input: QLineEdit
    category_input: QComboBox
    comment_input: QLineEdit

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QFormLayout()

        self.date_input = self._register_input_form("Дата", layout, DateWidget())
        self.amount_input = self._register_input_form("Сумма", layout, QLineEdit())
        self._register_category_input_form(layout)
        self.comment_input = self._register_input_form("Комментарий", layout, QLineEdit())

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self._register_buttons()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.buttonBox)
        self.setLayout(main_layout)

    @Slot()
    def ok_button_click(self):
        self.is_ok_clicked = True
        self.accept()

    def exec(self):
        super().exec()

    def _register_buttons(self):
        ok_button = QtWidgets.QDialogButtonBox.StandardButton.Ok
        cancel_button = QtWidgets.QDialogButtonBox.StandardButton.Cancel
        self.buttonBox.addButton(ok_button)
        self.buttonBox.addButton(cancel_button)

        self.buttonBox.accepted.connect(self.ok_button_click)
        self.buttonBox.rejected.connect(self.reject)

    @staticmethod
    def _register_input_form(text: str,
                             layout: QFormLayout,
                             widget: QWidget) -> QWidget:
        label_with_text = QtWidgets.QLabel(text)
        layout.addRow(label_with_text, widget)
        return widget

    # TODO IMPLEMENT
    def _register_category_input_form(self,
                                      layout: QFormLayout):
        label_with_text = QtWidgets.QLabel("Категория")
        self.category_input.setPlaceholderText('Выбрать')
        self.category_input.addItems(self.ctg_options)

    def get_data_from_forms(self) -> dict:
        date: str = self.date_input.date().toString('dd-MM-yyyy')
        amount: int = int(self.amount_input.text())
        category: int = int(self.category_input.currentIndex())
        comment: str = self.comment_input.text()
        return {"expense_date": date, "amount": amount, "category": category, "comment": comment}

    def set_categories(self, categories: list[(str, str)]):
        self.category_input.addItems([c.name for c in categories])
