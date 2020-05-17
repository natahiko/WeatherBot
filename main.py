import telebot
import requests
from pyowm import OWM
import subprocess
from resources import *
from utils import DataBase, ParserConfig
import os

path = os.path.dirname(os.path.abspath(__file__))

# load config with all dispatchers
config = ParserConfig(os.path.join(path, 'config', 'config.json'))

# run the timer for everyday weather
command = ['python.exe', './resources/schedule_timer.py']
p = subprocess.Popen(command)

# create connection and cursor for using in other methods
mydb = DataBase(**config['database'])

# create bot and APIID variable
bot = telebot.TeleBot(config['token'])
APPID = config['APPID']

# create new owm object
owm = OWM(APPID)
functions = Functions(bot, mydb, APPID, owm)


@bot.message_handler(commands=['changecity'])
def handle_ch(message):
    send = bot.send_message(message.chat.id, 'Please, print your cityname (in English): ')
    bot.register_next_step_handler(send, functions.changecity)


@bot.message_handler(commands=['start'])
def start_message(message):
    functions.start_message(message)


# command to find current weather in user's city
@bot.message_handler(commands=['now'])
def handle_now(message):
    usercityid = methods.get_city_id(message.chat.id, mydb)
    data = owm.weather_at_id(int(usercityid))
    w = data.get_weather()
    mess = "Now weather: " + methods.get_weather_from_owm(w)
    bot.send_message(message.chat.id, mess)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, methods.get_help_text())


# command to find current weather in any city
@bot.message_handler(commands=['nowat'])
def handle_nowat(message):
    return functions.handle_nowat(message)


# the weather for all day for tomorrow
@bot.message_handler(commands=['tomorrow'])
def handle_tomorrow(message):
    return functions.handle_tomorrow(message)


# the weather for the rest of current day
@bot.message_handler(commands=['today'])
def handle_today(message):
    cityid = methods.get_city_id(message.chat.id, mydb)
    functions.handle_today(message, cityid)


# to know weather for the one of next 5 day
@bot.message_handler(commands=['wday'])
def handle_wday(message):
    return functions.handle_wday(message)


# mathod to know weather in any time in one of next 5 day
@bot.message_handler(commands=['wtime'])
def handle_wtime(message):
    return functions.handle_wtime(message)


@bot.message_handler(content_types=['text'])
def send_text(message):
    return functions.send_text(message)


bot.polling(none_stop=True, interval=0)
