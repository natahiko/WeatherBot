import telebot
import requests
import datetime
from pyowm import OWM
import mysql.connector
import subprocess
from app.resources.methods import methods

# run the timer for everyday weather
command = ['python.exe', 'schedule_timer.py']
p = subprocess.Popen(command)

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


@bot.message_handler(commands=['changecity'])
def handle_ch(message):
    send = bot.send_message(message.chat.id, 'Please, print your cityname (in English): ')
    bot.register_next_step_handler(send, changecity)


def changecity(message):
    # try to find such city
    r = requests.get('http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID={}'.format(message.text, APPID))
    if (r.json()['count'] == 0):
        send = bot.send_message(message.chat.id,
                                'Uncorrect city name. If you want to try again use command /changecity')
    else:
        # if all is correct add ne user to database
        mycursor = mydb.cursor()
        sql = "UPDATE users SET cityid = %s WHERE userid = %s"
        val = (r.json()['list'][0]['id'], message.chat.id)
        mycursor.execute(sql, val)
        mydb.commit()
        bot.send_message(message.chat.id,
                         "You successfully changed your city!")


@bot.message_handler(commands=['start'])
def start_message(message):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users WHERE userid = {}".format(message.chat.id))
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        get_city(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Hello!")


# method for get user cityname and check it more than 1 time
def get_city(id):
    send = bot.send_message(id, 'Please, print your cityname (in English): ')
    bot.register_next_step_handler(send, city)


def city(message):
    # try to find such city
    r = requests.get('http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID={}'.format(message.text, APPID))
    if (r.json()['count'] == 0):
        # if such city unknown for the OWM we ask to print cityname one more time
        get_city(message.chat.id)
    else:
        # if all is correct add ne user to database
        mycursor = mydb.cursor()
        sql = "INSERT INTO users (userid, cityid) VALUES (%s, %s)"
        val = (message.chat.id, r.json()['list'][0]['id'])
        mycursor.execute(sql, val)
        mydb.commit()
        bot.send_message(message.chat.id,
                         "Congradulations! You're ready to use me) \nI will send you information about weather everyday at 7:00 \n \nUse command /help to see all command")


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
    cityname = message.text[7:]
    if cityname == '': return
    r = requests.get('http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID={}'.format(cityname, APPID))
    if (r.json()['count'] == 0):
        bot.send_message(message.chat.id, "Uncorect city. To try again write /nowat [cityname]")
    else:
        data = owm.weather_at_place(cityname)
        w = data.get_weather()
        mess = "Todays weather in " + cityname.upper() + " " + methods.get_weather_from_owm(w)
        bot.send_message(message.chat.id, mess)


# the weather for all day for tomorrow
@bot.message_handler(commands=['tomorrow'])
def handle_tomorrow(message):
    cityid = methods.get_city_id(message.chat.id, mydb)
    r = requests.get('http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, APPID))
    data = r.json()['list']
    today = datetime.date.today() + datetime.timedelta(days=1)
    mess = "Weather for tomorrow (" + str(today.day) + "." + str(today.month) + "): \n" + str(
        methods.get_day_weather(2, data))
    bot.send_message(message.chat.id, mess)


# the weather for the rest of current day
@bot.message_handler(commands=['today'])
def handle_tomorrow(message):
    cityid = methods.get_city_id(message.chat.id, mydb)
    r = requests.get('http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, APPID))
    mess = "Todays weather: \n" + str(methods.get_day_weather(1, r.json()['list']))
    bot.send_message(message.chat.id, mess)


# to know weather for the one of next 5 day
@bot.message_handler(commands=['wday'])
def handle_wday(message):
    # create keyboard with datas
    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
    today = datetime.datetime.now()
    t1 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t2 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t3 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t4 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t5 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    keyboard1.row(t1, t2, t3, t4, t5)
    bot.send_message(message.chat.id, "Choose day: ", reply_markup=keyboard1)


# mathod to know weather in any time in one of next 5 day
@bot.message_handler(commands=['wtime'])
def handle_wtime(message):
    keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
    today = datetime.datetime.now()
    t1 = "at " + str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t2 = "at " + str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t3 = "at " + str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t4 = "at " + str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t5 = "at " + str(today.day) + "." + str(today.month) + "." + str(today.year)
    keyboard1.row(t1, t2, t3, t4, t5)
    bot.send_message(message.chat.id, "Choose day: ", reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    cityid = methods.get_city_id(message.chat.id, mydb)
    r = requests.get(
        'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, APPID))
    data = r.json()['list']
    # create variables with the next 5 day
    today = datetime.datetime.now()
    t1 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t2 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t3 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t4 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    today = today + datetime.timedelta(days=1)
    t5 = str(today.day) + "." + str(today.month) + "." + str(today.year)
    # create array with different hour
    time_mess_array = []
    for x in range(0, 23, 3):
        if x < 10:
            res = "0" + str(x) + ":00 - "
            if (x + 3) < 10: res += "0"
            res += str(x + 3) + ":00 "
        else:
            res = str(x) + ":00 - " + str(x + 3) + ":00 "
        time_mess_array.append(res)

    # chexk for the message from command /wday
    if message.text.lower() == t1:
        mess = "The weather at " + t1 + ": \n" + methods.get_day_weather(1, data)
        bot.send_message(message.chat.id, mess)
        return
    elif message.text.lower() == t2:
        mess = "The weather at " + t2 + ": \n" + methods.get_day_weather(2, data)
        bot.send_message(message.chat.id, mess)
        return
    elif message.text.lower() == t3:
        mess = "The weather at " + t3 + ": \n" + methods.get_day_weather(3, data)
        bot.send_message(message.chat.id, mess)
        return
    elif message.text.lower() == t4:
        mess = "The weather at " + t4 + ": \n" + methods.get_day_weather(4, data)
        bot.send_message(message.chat.id, mess)
        return
    elif message.text.lower() == t5:
        mess = "The weather at " + t5 + ": \n" + methods.get_day_weather(5, data)
        bot.send_message(message.chat.id, mess)
        return
    # check for the command /wtime
    query = message.text.lower()
    for x in time_mess_array:
        if query.startswith(x):
            mes = query[14:]
            if mes == "at " + t1 or mes == "at " + t2 or mes == "at " + t3 or mes == "at " + t4 or mes == "at " + t5:
                send_weather_at_time(message)
                return
    # check if it was day message from command /wtime and make keyboakd for time query
    if query == "at " + t1 or query == "at " + t2 or query == "at " + t3 or query == "at " + t4 or query == "at " + t5:
        keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
        if int(message.text[3:5]) == today.day - 4:
            for x in time_mess_array:
                if int(x[8:10]) > today.hour:
                    keyboard2.row(x + message.text)
        else:
            for x in time_mess_array:
                keyboard2.row(x + message.text)
        bot.send_message(message.chat.id, "Choose time: ", reply_markup=keyboard2)
        return

    # send stiker to user if he print not command
    bot.send_sticker(message.chat.id, 'CAADAgADPgIAAkcVaAnaG0eZ4kbcKwI')


# additional method to make and send text message current weather
def send_weather_at_time(message):
    cityid = methods.get_city_id(message.chat.id, mydb)
    r = requests.get(
        'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, APPID))
    data = r.json()['list']
    today = datetime.datetime.now()
    now_hour = int(round((24 - today.day) / 3)) + 1
    day = int(message.text[17:19]) - today.day + 1
    if day == 1:
        data = data[0 + now_hour - 1]
    else:
        data = data[day * 8 - 8 + now_hour + int(round((24 / int(message.text[0:2]))))]
    result = "The weather " + message.text[0:13] + " (" + message.text[17:24] + "): \n"
    result += "{} {} ({})\n🌡 {}° {} {}m/s \nPresure: {}mm".format(data['weather'][0]['main'],
                                                                   methods.get_weather_icon(data['weather'][0]['icon']),
                                                                   data['weather'][0]['description'],
                                                                   int(round(data['main']['temp'] - 273, 15)),
                                                                   methods.get_wind_smiley(data['wind']['deg']),
                                                                   data['wind']['speed'],
                                                                   int(round(data['main']['pressure'] * 0.75)))
    bot.send_message(message.chat.id, result)


bot.polling(none_stop=True, interval=0)
