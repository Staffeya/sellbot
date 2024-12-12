import threading
import asyncio
from bot_seller import start_bot_seller
from stripe_webhook import start_webhook_server

def run_flask():
    """Функция для запуска Flask-сервера"""
    start_webhook_server()

def run_bot_seller():
    """Функция для запуска Telegram бота с ручным созданием event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_bot_seller()

if __name__ == "__main__":
    # Создаём потоки для Flask и Telegram бота
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    bot_thread = threading.Thread(target=run_bot_seller, daemon=True)

    # Запускаем оба потока
    flask_thread.start()
    bot_thread.start()

    # Ждем завершения потоков
    flask_thread.join()
    bot_thread.join()
