import telebot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import config  # Importing the config module

rpc_connection = AuthServiceProxy(f'http://{config.rpc_user}:{config.rpc_password}@127.0.0.1:8276')

bot_token = config.TOKEN  # Assuming you have config.TOKEN defined somewhere
bot = telebot.TeleBot(bot_token)

def address_balance(args):
    inputs = rpc_connection.listunspent(0, 9999, args)
    balance = 0
    if len(inputs) == 0:
        balance += 0
    elif len(inputs) == 1:
        balance += inputs[0].get("amount")
    else:
        for i in inputs:
            balance += i.get("amount")
    return balance

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
    global temp
    args = message.text.split()[1:]
    if len(args) != 3:
        bot.reply_to(message, "Template: /send <sender_address> <receiver_address> <amount>")
        return
    sender_address, receiver_address, amount = args
    try:
        inputs = rpc_connection.listunspent(0, 9999, [sender_address])
    except JSONRPCException:
        bot.reply_to(message, f"Incorrect sender wallet address")
        return

    for i in inputs:
        temp = i
        if float(float(temp.get("amount"))) > (float(amount)+0.001):
            break
    if float(float(temp.get("amount"))) < (float(amount)+0.001):
        bot.reply_to(message, "Insufficient funds")
        return
    fee = float(temp.get("amount")) - float(amount) - 0.001
    inputForTransaction = {"txid":temp.get("txid"), "vout": temp.get("vout")}
    try:
        createTransaction = rpc_connection.createrawtransaction([inputForTransaction], {receiver_address:amount, sender_address:fee})
    except JSONRPCException:
        bot.reply_to(message, f"Incorrect receiver wallet address")
        return
    signTransaction = rpc_connection.signrawtransaction(createTransaction)
    receivedHex = signTransaction.get("hex")
    txid = rpc_connection.sendrawtransaction(receivedHex)
    bot.reply_to(message, f"Coins sent to the receiver! Transaction ID: {txid}")

@bot.message_handler(commands=['getaddressbalance'])
def get_address_balance(message):
    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "Template: /getaddressbalance <wallet_address>")
        return
    try:
        balance = address_balance(args)
    except JSONRPCException:
        bot.reply_to(message, f"Incorrect wallet address ")
        return
    bot.reply_to(message, f"Address balance: {balance} KZC")

@bot.message_handler(commands=['getalladdressesbalance'])
def get_all_addresses_balance(message):
    total_balance = get_total_balance()
    bot.reply_to(message, f"Total balance of all addresses: {total_balance} KZC")

@bot.message_handler(content_types=['text'])
def send_message(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.infinity_polling()
