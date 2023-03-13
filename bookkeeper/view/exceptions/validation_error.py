

class ValidationError(Exception):

    def __init__(self, param: str):
        self.message = \
            'Поле ' + param + 'должно быть заполнено'

        super().__init__()
