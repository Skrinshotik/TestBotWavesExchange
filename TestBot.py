from logging import exception
import requests
import pywaves as pw
import telebot
import ccxt
from telebot import types

we = ccxt.wavesexchange({
    'apiKey': 'PUBLIC KEY',
    'secret': 'PRIVATE KEY',
    'enableRateLimit': True,
})

bot = telebot.TeleBot('5808235694:AAE8_zfJJ1Jqh5JQQXQEkpXGd_g6bJXDjT0');
amount_in = 0
price_in = 0
operation = 0

@bot.message_handler(content_types=['text'])
def start(message):
    try:
        if message.text == '/start':
            bot.send_message(message.chat.id, 'test bot - WavesExchange');
            callback_task(message)
        else:
            bot.send_message(message.chat.id, 'write /start');
    except Exception:
        bot.send_message(message.chat.id, 'Something went wrong  : (')        
        
def callback_task(message):
    keyboard = types.InlineKeyboardMarkup();
    key_price = types.InlineKeyboardButton(text='BTC/USDT', callback_data= 'price');
    key_buy_usdt= types.InlineKeyboardButton(text='BTC --> USDT', callback_data= "buy_usdt");
    key_buy_btc= types.InlineKeyboardButton(text='USDT --> BTC', callback_data= "buy_btc");
    keyboard.add(key_price, key_buy_usdt, key_buy_btc);
    bot.send_message(message.chat.id, 'Choose option', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def amount_input(message):
    amount_in = message.text
    bot.send_message(message.chat.id, 'Enter price:');
    bot.register_next_step_handler(message, price_input)

@bot.message_handler(content_types=['text'])
def price_input(message):
    price_in = message.text    
    transaction(message)

@bot.message_handler(content_types=['text'])
def transaction(message):
    side = ''
    if(operation == 1):
        side = 'buy'
    elif(operation == 2):
        side = 'sell'
    we.load_markets()   

    # пытался прописать обработку исключения, но постоянно выбивало новое исключение с ошибкой доступа по запросу к ресурсу, связанному с WavesX
    #try:
    #    order = we.createOrder('BTC/USDT', 'limit', side, amount_in, price_in)
    #    bot.send_message(message.chat.id, 'Transaction was successful');
    #except ccxt.InsufficientFunds:
    #    bot.send_message(message.chat.id, 'Something went wrong  : (') 

    try:
        order = we.createOrder('BTC/USDT', 'limit', side, amount_in, price_in)
        bot.send_message(message.chat.id, 'Transaction was successful');
    except Exception:
        bot.send_message(message.chat.id, 'Something went wrong  : (') 

    callback_task(message)
    

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "price":
        we.load_markets()
        price = we.fetch_ticker('BTC/USDT')['last']
        bot.send_message(call.message.chat.id, f'Current price of BTC/USDT --> {price}');  
        callback_task(call.message)     
        
    elif call.data == "buy_btc":
        bot.send_message(call.message.chat.id, 'Enter amount:');
        operation = 1
        bot.register_next_step_handler(call.message, amount_input)

    elif call.data == "buy_usdt":
        bot.send_message(call.message.chat.id, 'Enter amount:');
        operation = 2
        bot.register_next_step_handler(call.message, amount_input)

        

bot.polling(none_stop=True, interval=0)
