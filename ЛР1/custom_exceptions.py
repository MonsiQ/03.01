class MissingVariable(Exception):
    '''Срабатывает, когда отсутствует одна из переменных окружения .env'''

    def __init__(self, variable_name=''):
        # Инициализация класса исключений с именем переменной
        self.variable_name = variable_name

    def __str__(self):
        # Возвращает строковое представление ошибки
        return f'Переменная {self.variable_name} отсутствует в файле .env'
