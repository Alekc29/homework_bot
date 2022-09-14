import exceptions
import logging
import os
import requests
import sys
import time

from dotenv import load_dotenv
from http import HTTPStatus
from telegram import Bot, error

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACT_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGA_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGA_ID_TOKEN')

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат.
    Определяемый переменной окружения TELEGRAM_CHAT_ID.
    Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
    try:
        logging.info('Сообщение подготовлено к отправке.')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Сообщение отправлено')
    except Exception:
        raise error.TelegramError('Сообщение застряло.')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса.
    В качестве параметра функция получает временную метку.
    В случае успешного запроса должна вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logging.info('Активирована get_api_answer.')
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if homework_statuses.status_code == HTTPStatus.OK:
        logging.info('Запрос данных пройзведён.')
        return homework_statuses.json()
    raise exceptions.RequestsError(
        f'Ошибка сервера: {ENDPOINT}, auth: {HEADERS}'
    )


def check_response(response):
    """Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API.
    Приведенный к типам данных Python.
    Если ответ API соответствует ожиданиям,
    то функция должна вернуть список домашних работ
    (он может быть и пустым), доступный в ответе API по ключу 'homeworks'.
    """
    logging.info('Проверка данных запроса.')
    if not isinstance(response, dict):
        raise TypeError(f'Ответ является {type(response)}, а не словарем.')
    if response.get('homeworks') is None:
        raise KeyError('Ключа homeworks в словаре нету.')
    if type(response['homeworks']) == list and len(response['homeworks']) > 0:
        return response['homeworks']
    raise KeyError(f'{response["homeworks"]} некорректный список.')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один
    элемент из списка домашних работ. В случае успеха, функция
    возвращает подготовленную для отправки в Telegram строку,
    содержащую один из вердиктов словаря HOMEWORK_STATUSES.
    """
    logging.info('Парсинг статуса.')
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except Exception:
        raise KeyError(f'ключ не найден {homework}')
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    raise exceptions.StatusError('Неизвестный статус.')


def check_tokens():
    """Проверяет доступность переменных окружения.
    Которые необходимы для работы программы.
    Если отсутствует хотя бы одна переменная окружения —
    функция должна вернуть False, иначе — True.
    """
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        TOKEN_error = []
        if not PRACTICUM_TOKEN:
            TOKEN_error.append('PRACTICUM_TOKEN')
        if not TELEGRAM_TOKEN:
            TOKEN_error.append('TELEGRAM_TOKEN')
        if not TELEGRAM_CHAT_ID:
            TOKEN_error.append('TELEGRAM_CHAT_ID')
        logging.critical(f'Не хватает ТОКЕНов! Проверьте {TOKEN_error}.')
        sys.exit()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    message_old = 'Я начал свою работу.'
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework[0])
            current_timestamp = int(time.time())
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            message = f'Сбой в работе программы: {error}'
        finally:
            if message != message_old:
                send_message(bot, message)
            message_old = message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
