from logging import exception
import pywaves as pw
import telebot
import ccxt
from telebot import types


# Объявление глобальных переменных
we = ccxt.wavesexchange({
    'apiKey': 'PUBLIC KEY',
    'secret': 'PRIVATE KEY',
    'enableRateLimit': True,
})
bot = telebot.TeleBot('5808235694:AAE8_zfJJ1Jqh5JQQXQEkpXGd_g6bJXDjT0');
amount_in = 0
price_in = 0
side = '' 

#Стартовая функция бота
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
        
#Вывод сообщения с клавиатурой, для вызова определенных функций
def callback_task(message):
    keyboard = types.InlineKeyboardMarkup();
    key_price = types.InlineKeyboardButton(text='BTC/USDT', callback_data= 'price');
    key_buy_usdt= types.InlineKeyboardButton(text='BTC --> USDT', callback_data= "buy_usdt");
    key_buy_btc= types.InlineKeyboardButton(text='USDT --> BTC', callback_data= "buy_btc");
    keyboard.add(key_price, key_buy_usdt, key_buy_btc);
    bot.send_message(message.chat.id, 'Choose option', reply_markup=keyboard)

#Обработка пользовательского ввода количества валюты
@bot.message_handler(content_types=['text'])
def amount_input(message):
    global amount_in
    amount_in = message.text
    bot.send_message(message.chat.id, 'Enter price:');
    bot.register_next_step_handler(message, price_input)

#Обработка пользовательского ввода цены валюты
@bot.message_handler(content_types=['text'])
def price_input(message):
    global price_in
    price_in = message.text    
    transaction(message)

#Совершение выбранной пользователем транзакции
@bot.message_handler(content_types=['text'])
def transaction(message):
    we.load_markets()   

    # пытался прописать обработку исключения, но постоянно выбивало новое исключение с ошибкой доступа по запросу к ресурсу, связанному с WavesX
    #try:
    #    order = we.createOrder('BTC/USDT', 'limit', side, amount_in, price_in)
    #    bot.send_message(message.chat.id, 'Transaction was successful');
    #except ccxt.InsufficientFunds:
    #    bot.send_message(message.chat.id, 'Something went wrong  : (') 

    try:
        order = we.createOrder('BTC/USDT', 'limit', side, amount_in, price_in)['id']
        bot.send_message(message.chat.id, 'Transaction was successful' + f'\nOrder id: {order}');
    except Exception:
        bot.send_message(message.chat.id, 'Something went wrong  : (') 
    callback_task(message)
    
#Обработка нажитий на кнопки из функции callback_task
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global side

    #Вывод актуальной цены на бирже
    if call.data == "price":
        we.load_markets()
        price = we.fetch_ticker('BTC/USDT')['last']
        bot.send_message(call.message.chat.id, f'Current price of BTC/USDT --> {price}');  
        callback_task(call.message)     
        
    #Покупка BTC/USDT
    elif call.data == "buy_btc":
        bot.send_message(call.message.chat.id, 'Enter amount:');
        side = 'buy'
        bot.register_next_step_handler(call.message, amount_input)

    #Продажа BTC/USDT
    elif call.data == "buy_usdt":
        bot.send_message(call.message.chat.id, 'Enter amount:');
        side = 'sell'
        bot.register_next_step_handler(call.message, amount_input)

        

bot.polling(none_stop=True, interval=0)
