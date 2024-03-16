import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import config

rpc_connection = AuthServiceProxy(f'http://{config.rpc_user}:{config.rpc_password}@127.0.0.1:8276')

bot_token = config.TOKEN
bot = telebot.TeleBot(bot_token)

def address_balance(address):
    inputs = rpc_connection.listunspent(0, 9999, [address])
    balance = sum(input_.get("amount") for input_ in inputs)
    return balance

def all_addresses_balance():
    addresses = rpc_connection.getaddressesbyaccount("")  # Fetch all addresses in the wallet
    balances = {}
    for address in addresses:
        balance = address_balance(address)
        balances[address] = balance
    return balances

@bot.message_handler(commands=['getnewaddress'])
def get_new_address(message):
    new_address = rpc_connection.getnewaddress()
    bot.reply_to(message, f"New address: {new_address}")

@bot.message_handler(commands=['getbalance'])
def get_balance(message):
    balance = rpc_connection.getbalance()
    bot.reply_to(message, f"Total wallet balance: {balance}")

@bot.message_handler(commands=['send'])
def send_coins(message):
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, "Template: /send <sender_address> <receiver_address> <amount>")
        return
    sender_address, receiver_address, amount = args
    # Your transaction sending logic here

@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Template: /getaddressbalance <wallet_address>")
        return
    address = args[0]
    try:
        balance = address_balance(address)
        bot.reply_to(message, f"Address balance: {balance} KZC")
    except JSONRPCException:
        bot.reply_to(message, f"Incorrect wallet address ")

@bot.message_handler(commands=['getalladdressesbalance'])
def get_all_addresses_balance(message):
    balances = all_addresses_balance()
    response = "Balances of all addresses:\n"
    for address, balance in balances.items():
        response += f"{address}: {balance} KZC\n"
    bot.reply_to(message, response)

@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.infinity_polling()
