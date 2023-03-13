from PySide6.QtWidgets import QTableWidgetItem

from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.validator import Validator


class Mapper:

    def __init__(self):
        pass

    @staticmethod
    # TODO need to introduce new constructor for Budget
    def table_item_to_budget(item: QTableWidgetItem) -> Budget:
        total_amount = int(item.text())
        pk = item.row()
        consumed_amount = 0
        period = None
        budget = Budget(total_amount, consumed_amount, period, pk)
        Validator.validate_budget(budget)
        return budget
