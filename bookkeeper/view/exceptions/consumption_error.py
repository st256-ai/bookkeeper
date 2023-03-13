from bookkeeper.models.budget import Period


class ConsumptionOverflowError(Exception):

    def __init__(self, period: Period) -> None:
        self.message = f'Бюджет за {self.map_to_str(period)} превышен!'
        super().__init__(self.message)

    @staticmethod
    def map_to_str(period: Period) -> str:
        if period == Period.DAY:
            return 'день'
        elif period == Period.WEEK:
            return 'неделю'
        else:
            return 'месяц'
