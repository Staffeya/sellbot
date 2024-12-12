from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import sqlite3
import stripe
import os

# Инициализация бота
API_TOKEN = "7682116820:AAFBMQE1vvi8KhjlIMyRPzpeVWxJuT-gEDI"  # Замени на свой токен
stripe.api_key = "sk_test_51QUQGNALZk2185tZWDxL8VX9DF2tnbXLLTRVVTKRTEsffh9G6LJL7Wnuc0sHzzGqYMwPa79pPcyATZMZnDvs2oop00DISVKF5X"  # Замени на свой Stripe ключ

# URL для возврата после оплаты
SUCCESS_URL = "https://example.com/success"
CANCEL_URL = "https://example.com/cancel"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Создание базы данных
def setup_database():
    conn = sqlite3.connect("tenants.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            subscription_active INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Проверка подписки
def check_subscription(telegram_id):
    conn = sqlite3.connect("tenants.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_active FROM tenants WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

# Стартовая команда
def start_bot_seller():
    @dp.message_handler(commands=['start'])
    async def welcome(message: types.Message):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("🛒 Register Store"), KeyboardButton("💳 Buy Subscription"))
        await message.answer("👋 Welcome to the Bot Store!", reply_markup=markup)

    print("Bot Seller is running...")
    executor.start_polling(dp, skip_updates=True)

# Регистрация арендатора
@dp.message_handler(lambda message: message.text == "🛒 Register Store")
async def register_store(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    conn = sqlite3.connect("tenants.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE telegram_id = ?", (telegram_id,))
    tenant = cursor.fetchone()

    if tenant:
        await message.answer("✅ You are already registered! Use /subscribe to activate your subscription.")
    else:
        cursor.execute("INSERT INTO tenants (telegram_id, username) VALUES (?, ?)", (telegram_id, username))
        conn.commit()
        await message.answer("📝 Registration complete! Use /subscribe to activate your store.")
    conn.close()

# Генерация ссылки для оплаты
@dp.message_handler(lambda message: message.text == "💳 Buy Subscription")
async def buy_subscription(message: types.Message):
    telegram_id = message.from_user.id

    if check_subscription(telegram_id):
        await message.answer("✅ You already have an active subscription!")
        return

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Bot Shop Subscription", "description": "1-month bot subscription."},
                    "unit_amount": 1000,  # Цена $10.00 в центах
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
            metadata={"telegram_id": telegram_id}
        )
        await message.answer(f"💳 Click the link to complete your payment:\n{checkout_session.url}")
    except Exception as e:
        print(f"Error creating Stripe session: {e}")
        await message.answer("❌ Failed to create payment session. Please try again later.")

if __name__ == "__main__":
    setup_database()
    print("Bot Seller is running...")
    executor.start_polling(dp, skip_updates=True)
    start_bot_seller()
