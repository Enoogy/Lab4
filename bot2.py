import config
import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

bot = telebot.TeleBot(config.token)

# Подключение к RPC-серверу Bitcoin
rpc_connection = AuthServiceProxy(config.rpc_url)

# Функция для генерации нового адреса
def get_new_address():
    try:
        new_address = rpc_connection.getnewaddress()
        return new_address
    except JSONRPCException as e:
        return f"Ошибка при генерации нового адреса: {e}"

# Функция для получения баланса
def get_balance():
    try:
        balance = rpc_connection.getbalance()
        return balance
    except JSONRPCException as e:
        return f"Ошибка при получении баланса: {e}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот. Как я могу помочь вам?")

@bot.message_handler(commands=['getnewaddress'])
def send_new_address(message):
    new_address = get_new_address()
    bot.send_message(message.chat.id, f"Новый адрес: {new_address}")

@bot.message_handler(commands=['getbalance'])
def send_balance(message):
    balance = get_balance()
    bot.send_message(message.chat.id, f"Баланс кошелька: {balance} BTC")

if __name__ == '__main__':
    bot.infinity_polling()
