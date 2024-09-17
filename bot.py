from time import sleep
from requests import post

UPDATES_URL = "https://botapi.messenger.yandex.net/bot/v1/messages/getUpdates"  # URL для получения обновлений
SEND_TEXT_URL = "https://botapi.messenger.yandex.net/bot/v1/messages/sendText/"  # URL для отправки текста

# В заголовке указываем токен бота
HEADERS = {
    "Authorization": "OAuth ТОКЕН_БОТА",
    "ContentType": "application/json"
}


# Функция которая периодически запрашивает наличие новых сообщений для бота. В качестве аргумента передаем функцию
# которая будет вызвана при получении новых сообщений
def start_pooling(bot_fn):
    #  Запускаем цикл постоянных запросов на новые сообщения
    last_update_id = -1

    while True:
        # Запрашиваем новые сообщения. Будут получены сообщения только с ID на 1 больше последнего полученного
        # сообщения
        request_body = {'limit': 100, 'offset': last_update_id + 1}

        response = post(UPDATES_URL, json=request_body, headers=HEADERS)
        updates = response.json()['updates']  # из ответа получаем массив новых сообщений

        if len(updates) > 0:
            # Для последующих запросов цикла сохраняем ID последнего сообщения
            last_update_id = int(updates[len(updates) - 1]['update_id'])

            # Для каждого сообщения вызываем функцию которая будет обрабатывать это сообщение
            for update in updates:
                print(update)  # Выводим в командную строку полученное обновление
                bot_fn(update)
        sleep(1)  # Ждем 1 секунду прежде чем повторить цикл


# Функция которая будет отправлять сообщения от имени бота
def send_text(update):
    # В тело запроса для отправки сообщения добавляем исходный текст сообщения
    request_body = {'text': 'Вы написали: ' + update['text']}
    if update['chat']['type'] == 'group':  # Если исходное сообщение отправлено в групповой чат, то отвечаем в него
        request_body.update({'chat_id': update['chat']['id']})

    elif update['chat']['type'] == 'private':  # Если сообщение отправлено персонально боту, то отвечаем лично
        request_body.update({'login': update['from']['login']})

    post(SEND_TEXT_URL, json=request_body, headers=HEADERS)  # отправляем сообщение


# Функция бота, которая вызывается каждый раз при получении новых обновлений
def bot(update):
    send_text(update)  # В нашем примере мы отправляем текст при новых обновлениях


if __name__ == '__main__':
    start_pooling(bot)  # Запускаем функцию получения новых обновлений
