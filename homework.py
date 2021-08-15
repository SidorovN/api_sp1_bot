import logging
import os
import time
import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='./main.log', filemode='a'
)

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

STATUSES = {
    'approved': 'Ревьюеру всё понравилось, работа зачтена!',
    'rejected': 'К сожалению, в работе нашлись ошибки.',
}

CURRENT_HOMEWORK = {
    'status': ''
}

bot = telegram.Bot(TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    verdict = STATUSES[homework['status']]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
        return homework_statuses.json()
    except Exception as e:
        logging.warning(f'Ошибка запроса: {e}')
        return None


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    logging.info('Бот запущен')
    current_timestamp = int(time.time())

    while True:

        try:
            time.sleep(5 * 60)
            homeworks = get_homeworks(current_timestamp)
            homework = homeworks.get('homeworks')[0]
            current_timestamp = homeworks.get('current_date')
            if not homework:
                continue
            if homework['status'] not in STATUSES:
                logging.info(f'Неизвестный статус: {homework["status"]}')
                continue

            if homework['status'] != CURRENT_HOMEWORK['status']:
                message = parse_homework_status(homework)
                send_message(message)
            logging.info(homework['status'])
            CURRENT_HOMEWORK['status'] = homework['status']

        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
