import schedule
import time
from pyowm import OWM
import mysql.connector
import telebot
import requests
import datetime
from app.resources.methods import methods

# create connection and cursor for using in other methods
mydb = mysql.connector.connect(
    host="db4free.net",
    user="natahiko",
    password="Shusha_2303",
    database="weather_bot"
)

# create bot and APIID variable
bot = telebot.TeleBot('711188874:AAErmj7qK8apEoXdyX263XIYjw4vwRvKoqc')
APPID = 'e03289d4e7fe780d26b085815c6570d3'
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

