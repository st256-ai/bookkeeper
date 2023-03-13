"""
Модель бюджета
"""

from dataclasses import dataclass
from enum import Enum

Period = Enum('Period', ["DAY", "WEEK", "MONTH"])


@dataclass(slots=True)
class Budget:
    """
    Сущность, моделирующая бюджет
    total_amount - сумма бюджета
    consumed_amount - потраченная сумма
    period - срок ограничения на сумму бюджета
    pk - id записи в базе данных (primary key)
    """

    total_amount: int
    consumed_amount: int
    period: Period
    pk: int = 0
