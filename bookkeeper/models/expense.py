"""
Описан класс, представляющий расходную операцию
"""

import datetime
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Expense:
    """
    Расходная операция.
    amount - сумма
    category - id категории расходов
    expense_date - дата расхода
    added_date - дата добавления в бд
    comment - комментарий
    pk - id записи в базе данных
    """
    amount: int
    category: int
    expense_date: datetime = field(default_factory=datetime.now)
    added_date: datetime = field(default_factory=datetime.now)
    comment: str = ''
    pk: int = 0

    def __init__(self):
        pass

    def modify_attr(self, attr: str, str_value: str) -> None:
        try:
            if attr == 'expense_date':
                self.expense_date = datetime.datetime.strptime(str_value, '%d%m%Y')
            elif attr == 'amount':
                self.amount = int(str_value)
            elif attr == 'category':
                self.category = int(str_value)
            else:
                self.comment = str_value
        except RuntimeError as ex:
            message = 'Не удалось обновить запись о расходах'
            raise RuntimeError(message, ex)
