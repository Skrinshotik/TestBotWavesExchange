from logging import exception
import pywaves as pw
import telebot
import ccxt
from telebot import types


# Объявление глобальных переменных
assetId = "8LQW8f7P5d5PZM7GtZEBgaqRPGSzS3DfPuiXrURJ4AJS"
yourAddress = "3PEZUy4L4BQgn9B7jpQ7sQm4j9RgsqsW2RH"
bot = telebot.TeleBot('BOT API')
amount_in = 0
price_in = 0

#Стартовая функция бота
@bot.message_handler(content_types=['text'])
def start(message):
    try:
        if message.text == '/start':
            bot.send_message(message.chat.id, 'test bot - WavesExchange')
            callback_task(message)
        else:
            bot.send_message(message.chat.id, 'write /start')
    except Exception:
        bot.send_message(message.chat.id, 'Something went wrong  : (')        
        
#Вывод сообщения с клавиатурой, для вызова определенных функций
def callback_task(message):
    keyboard = types.InlineKeyboardMarkup()
    key_price = types.InlineKeyboardButton(text='BTC/USDT', callback_data= 'price')
    key_buy_usdt= types.InlineKeyboardButton(text='Exchange BTC', callback_data= "transfer_BTC")
    keyboard.add(key_price, key_buy_usdt);
    bot.send_message(message.chat.id, 'Choose option', reply_markup=keyboard)

#Обработка пользовательского ввода количества валюты
@bot.message_handler(content_types=['text'])
def amount_input(message):
    global amount_in
    amount_in = message.text
    we.load_markets()
    price = we.fetch_ticker('BTC/USDT')['last']
    confirm_input = types.InlineKeyboardMarkup()
    confirmation = types.InlineKeyboardButton(text='Confirm!', callback_data= 'confirm')
    canceling = types.InlineKeyboardButton(text='Cancel', callback_data= 'cancel')
    confirm_input.add(confirmation, canceling)
    result = float(price)*float(amount_in)
    bot.send_message(message.chat.id, f'It will be - {result} USDT\n', reply_markup=confirm_input)

@bot.message_handler(content_types=['text'])
def redirect(message):
    global amount_in
    trans_url = types.InlineKeyboardMarkup()
    redirect_button = types.InlineKeyboardButton(text='Pay', url= f"https://waves.exchange/#send/{assetId}?recipient={yourAddress}&amount={amount_in}")
    canceling = types.InlineKeyboardButton(text='Cancel', callback_data= 'cancel')
    trans_url.add(redirect_button, canceling)
    bot.send_message(message.chat.id, f'1. Follow the link for payment \n2. Log in \n3. Confirm the transaction\n', reply_markup=trans_url)
    
   
#Обработка нажитий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global side

    #Вывод актуальной цены на бирже
    if call.data == "price":
        we.load_markets()
        price = we.fetch_ticker('BTC/USDT')['last']
        bot.send_message(call.message.chat.id, f'Current price of BTC/USDT --> {price}')
        callback_task(call.message)     
        
    #Покупка BTC/USDT
    elif call.data == "transfer_BTC":
        bot.send_message(call.message.chat.id, 'Enter amount:')
        bot.register_next_step_handler(call.message, amount_input)
        
    #Перенаправление на оплату
    elif call.data == "confirm":
        redirect(call.message)

    #Отмена операции и перенаправление в главное меню
    elif call.data == "cancel":
        callback_task(call.message) 

        

bot.polling(none_stop=True, interval=0)

