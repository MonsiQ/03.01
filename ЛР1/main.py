import logging  # Импортируем модуль для логирования
import os  # Импортируем модуль для работы с операционной системой
import time  # Импортируем модуль для работы со временем
from dotenv import load_dotenv  # Импортируем функцию для загрузки переменных окружения из .env файла
from pyrogram import Client  # Импортируем класс Client из библиотеки Pyrogram для работы с Telegram API
from custom_exceptions import MissingVariable  # Импортируем класс исключений, если переменные отсутствуют

# Логгинг
logging.basicConfig(
    level=logging.INFO,  # Устанавливаем уровень логирования (INFO)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Устанавливаем формат сообщений
)
logger = logging.getLogger(__name__)  # Создаем логгер для текущего модуля

# Загружаем переменные из .env
load_dotenv('.env')  # Загружаем переменные окружения из файла .env
API_ID = os.getenv('MY_API_ID')  # Получаем API ID из переменных окружения
API_HASH = os.getenv('MY_API_HASH_KEY')  # Получаем API HASH из переменных окружения
MY_ID = os.getenv('MY_ID')  # Получаем свой ID из переменных окружения
TARGET_ID = os.getenv('TARGET_ID')  # Получаем ID целевого пользователя из переменных окружения
RETRY_DELAY = os.getenv('RETRY_DELAY')  # Получаем задержку повторных попыток из переменных окружения

# Проверяем наличие всех необходимых переменных
required_variables = {
    'API_ID': API_ID,
    'API_HASH': API_HASH,
    'MY_ID': MY_ID,
    'TARGET_ID': TARGET_ID,
    'RETRY_DELAY': RETRY_DELAY
}
# Определяем отсутствующие переменные
missing_variable = {
    key for key, value in required_variables.items() if value is None
}
if missing_variable:
    # Если отсутствуют обязательные переменные, логируем сообщение и выбрасываем исключение
    logger.critical(
        'Отсутствуют следующие обязательные переменные в .env:'
        f'{", ".join(missing_variable)}'
    )
    raise MissingVariable(missing_variable)  # Выбрасываем исключение, если переменные отсутствуют

# Преобразуем переменные в целые числа, если они существуют
API_ID = int(API_ID)  # Преобразуем API_ID в целое число
MY_ID = int(MY_ID)  # Преобразуем свой ID в целое число
TARGET_ID = int(TARGET_ID)  # Преобразуем ID целевого пользователя в целое число
RETRY_DELAY = int(RETRY_DELAY)  # Преобразуем задержку повторных попыток в целое число

# Создаем экземпляр клиента
app = Client(
    'my_account',  # Имя сессии клиента
    api_id=API_ID,  # API ID
    api_hash=API_HASH  # API HASH
)

# Фильтруем все сообщения
@app.on_message()  # Декоратор, который обрабатывает входящие сообщения
async def forward_all_messages(client, message):
    try:
        user_id = message.from_user.id  # Получаем ID пользователя, отправившего сообщение
        user = await client.get_users(TARGET_ID)  # Получаем информацию о целевом пользователе
        username = (user.username  # Получаем имя пользователя
                    if user.username
                    else f'{user.first_name} {user.last_name}')  # Если имя пользователя отсутствует, используем полное имя
    except TypeError:
        time.sleep(RETRY_DELAY)  # Если произошла ошибка, ждем перед повторной попыткой

    while True:  # Бесконечный цикл для повторных попыток
        try:
            if user_id == TARGET_ID:  # Если сообщение от целевого пользователя
                await (client.send_message(MY_ID,  # Отправляем сообщение себе
                                           'Получено сообщение от '
                                           f'@{username}: {message.text}'))
            elif user_id == MY_ID:  # Если сообщение от самого себя
                await (client.send_message(MY_ID,  # Отправляем сообщение себе
                                           'Отправлено сообщение для '
                                           f'@{username}: {message.text}'))

            break  # Выходим из цикла, если отправлено сообщение
        except Exception as error:
            logger.error(f'Произошла ошибка: {str(error)}')  # Логируем ошибку
            logger.info(f'Повторная попытка через {RETRY_DELAY} секунд...')  # Логируем сообщение о повторной попытке
            time.sleep(RETRY_DELAY)  # Ждем перед следующей попыткой

if __name__ == '__main__':  # Если файл запущен как основной модуль
    app.run()  # Запускаем клиента