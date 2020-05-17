import schedule
import time
from pyowm import OWM
import telebot
import os
import requests
from resources import *
from utils import DataBase, ParserConfig

path = os.path.dirname(os.path.abspath(__file__))

# load config with all dispatchers
config = ParserConfig(os.path.join(path, '../config', 'config.json'))

# create connection and cursor for using in other methods
mydb = DataBase(**config['database'])

# create bot and APIID variable
bot = telebot.TeleBot(config['token'])
APPID = config['APPID']

# create new owm object
owm = OWM(APPID)


# send message to all users
def msg():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users")
    myresult = mycursor.fetchall()
    for x in myresult:
        x = str(x).replace(',', '')
        x = x[1:(len(x) - 1)].split()
        send_day_weather_to_user(x[1], x[2])


def send_day_weather_to_user(userid, cityid):
    r = requests.get(
        'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, APPID))
    data = r.json()['list']
    today = datetime.date.today() + datetime.timedelta(days=1)
    mess = "Weather for today ({0}.{1}): \n{2}".format(str(today.day), str(today.month), str(
        methods.get_day_weather(1, data)))
    bot.send_message(userid, mess)


# do method everyday at 7:00
schedule.every().day.at("07:00").do(msg)
while True:
    schedule.run_pending()
    time.sleep(10)
