import schedule
import time
from pyowm import OWM
import mysql.connector
import telebot
import requests
import datetime

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
        get_day_weather(1, data)))
    bot.send_message(userid, mess)


def get_weather_icon(icon):
    if icon == '01d' or icon == '01n': return '☀';
    if icon == '02d' or icon == '02n': return '⛅';
    if icon == '03d' or icon == '03n': return '☁';
    if icon == '04d' or icon == '04n': return '💨';
    if icon == '09d' or icon == '09n': return '🌧';
    if icon == '10d' or icon == '10n': return '🌦';
    if icon == '11d' or icon == '11n': return '⛈';
    if icon == '13d' or icon == '13n': return '❄';
    if icon == '50d' or icon == '50n': return '🌫';


def get_wind_smiley(deg):
    if deg > 350 or deg < 10: return '➡';
    if deg > 80 and deg < 100: return '⬆';
    if deg > 170 and deg < 190: return '⬅';
    if deg > 260 and deg < 280: return '⬇';
    if deg > 10 and deg < 80: return '↗';
    if deg > 100 and deg < 170: return '↖';
    if deg > 190 and deg < 260: return '↙';
    if deg > 280 and deg < 350: return '↘';


def get_day_weather(day, data):
    now_hour = int(int(round((24 - datetime.datetime.now().hour) / 3)) + 1)
    if day == 1:
        data = data[0:(now_hour + 1)]
        hour = 24 - now_hour * 3
    else:
        data = data[day * 8 - 8 + now_hour:day * 8 + now_hour]
        hour = 0
    result = ""
    for x in data:
        print([x][0])
        w = [x][0]
        if hour < 10: result += '0'
        result += str(hour) + ":00: {} {} ({})\n     🌡 {}° {} {}m/s \n".format(w['weather'][0]['main'],
                                                                                get_weather_icon(
                                                                                    w['weather'][0]['icon']),
                                                                                w['weather'][0]['description'],
                                                                                int(round(w['main']['temp'] - 273, 15)),
                                                                                get_wind_smiley(w['wind']['deg']),
                                                                                w['wind']['speed'])
        hour += 3
    return result

# do method everyday at 7:00
schedule.every().day.at("07:00").do(msg)
while True:
    schedule.run_pending()
    time.sleep(10)

