# Homework Bot

### Бот для проверки статуса домашней работы на код ревью в Яндекс.Практикум

## Технологии

- Python 3.7
- SimpleJWT
- Python-telegram-bot

## Запуск на ПК

У API Практикум.Домашка есть лишь один эндпоинт:

<https://practicum.yandex.ru/api/user_api/homework_statuses/>

и доступ к нему возможен только по токену.

Получить токен можно по [адресу](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a). Копируем его, он нам пригодится чуть позже.

### Принцип работы API

Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

    работа принята на проверку
    работа возвращена для исправления ошибок
    работа принята

### Запуск на ПК

Клонируем проект:
``` git clone https://github.com/Alekc29/homework_bot.git ```

Переходим в папку с ботом:
``` cd homework_bot ```

Устанавливаем виртуальное окружение:
``` python -m venv venv ```

Активируем виртуальное окружение:
``` source venv/bin/activate ```

Устанавливаем зависимости:
``` pip install -r requirements.txt ```

В консоле импортируем токены для ЯндексюПрактикум и для Телеграмм:

```
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID> 
```

 Запускаем бота:
``` python homework.py ```

Бот будет работать, и каждые 10 минут проверять статус вашей домашней работы.

Автор: Shiryaev Alekc
