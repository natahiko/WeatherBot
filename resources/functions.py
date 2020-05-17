from resources import methods
import requests
import datetime
import telebot


class Functions():
    def __init__(self, bot, mydb, APPID, owm):
        self.bot = bot
        self.mydb = mydb
        self.APPID = APPID
        self.owm = owm

    def handle_today(self, message, cityid):
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, self.APPID))
        mess = "Todays weather: \n" + str(methods.get_day_weather(1, r.json()['list']))
        self.bot.send_message(message.chat.id, mess)

    def start_message(self, message):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM users WHERE userid = {}".format(message.chat.id))
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            self.get_city(message.chat.id)
        else:
            self.bot.send_message(message.chat.id, "Hello!")

    # method for get user cityname and check it more than 1 time
    def get_city(self, id):
        send = self.bot.send_message(id, 'Please, print your cityname (in English): ')
        self.bot.register_next_step_handler(send, self.city)

    def city(self, message):
        # try to find such city
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID={}'.format(message.text, self.APPID))
        if (r.json()['count'] == 0):
            # if such city unknown for the OWM we ask to print cityname one more time
            self.get_city(message.chat.id)
        else:
            # if all is correct add ne user to database
            mycursor = self.mydb.cursor()
            sql = "INSERT INTO users (userid, cityid) VALUES (%s, %s)"
            val = (message.chat.id, r.json()['list'][0]['id'])
            mycursor.execute(sql, val)
            self.mydb.commit()
            self.bot.send_message(message.chat.id,
                                  "Congradulations! You're ready to use me) \nI will send you information about weather everyday at 7:00 \n \nUse command /help to see all command")

    def changecity(self, message):
        # try to find such city
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID={}'.format(message.text, self.APPID))
        if (r.json()['count'] == 0):
            send = self.bot.send_message(message.chat.id,
                                         'Uncorrect city name. If you want to try again use command /changecity')
        else:
            # if all is correct add ne user to database
            mycursor = self.mydb.cursor()
            sql = "UPDATE users SET cityid = %s WHERE userid = %s"
            val = (r.json()['list'][0]['id'], message.chat.id)
            mycursor.execute(sql, val)
            self.mydb.commit()
            self.bot.send_message(message.chat.id,
                                  "You successfully changed your city!")

    def handle_nowat(self, message):
        cityname = message.text[7:]
        if cityname == '': return
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/find?q={}&type=like&APPID={}'.format(cityname, self.APPID))
        if (r.json()['count'] == 0):
            self.bot.send_message(message.chat.id, "Uncorect city. To try again write /nowat [cityname]")
        else:
            data = self.owm.weather_at_place(cityname)
            w = data.get_weather()
            mess = "Todays weather in " + cityname.upper() + " " + methods.get_weather_from_owm(w)
            self.bot.send_message(message.chat.id, mess)

    def handle_tomorrow(self, message):
        cityid = methods.get_city_id(message.chat.id, self.mydb)
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, self.APPID))
        data = r.json()['list']
        today = datetime.date.today() + datetime.timedelta(days=1)
        mess = "Weather for tomorrow (" + str(today.day) + "." + str(today.month) + "): \n" + str(
            methods.get_day_weather(2, data))
        self.bot.send_message(message.chat.id, mess)

    def handle_wday(self, message):
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
        self.bot.send_message(message.chat.id, "Choose day: ", reply_markup=keyboard1)

    def handle_wtime(self, message):
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
        self.bot.send_message(message.chat.id, "Choose day: ", reply_markup=keyboard1)

    # additional method to make and send text message current weather
    def send_weather_at_time(self, message):
        cityid = methods.get_city_id(message.chat.id, self.mydb)
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, self.APPID))
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
                                                                       methods.get_weather_icon(
                                                                           data['weather'][0]['icon']),
                                                                       data['weather'][0]['description'],
                                                                       int(round(data['main']['temp'] - 273, 15)),
                                                                       methods.get_wind_smiley(data['wind']['deg']),
                                                                       data['wind']['speed'],
                                                                       int(round(data['main']['pressure'] * 0.75)))
        self.bot.send_message(message.chat.id, result)

    def send_text(self, message):
        cityid = methods.get_city_id(message.chat.id, self.mydb)
        r = requests.get(
            'http://api.openweathermap.org/data/2.5/forecast?id={}&type=like&APPID={}'.format(cityid, self.APPID))
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

        no_key_board = telebot.types.ReplyKeyboardRemove()
        # chexk for the message from command /wday
        if message.text.lower() == t1:
            mess = "The weather at " + t1 + ": \n" + methods.get_day_weather(1, data)
            self.bot.send_message(message.chat.id, mess, reply_markup=no_key_board)
            return
        elif message.text.lower() == t2:
            mess = "The weather at " + t2 + ": \n" + methods.get_day_weather(2, data)
            self.bot.send_message(message.chat.id, mess, reply_markup=no_key_board)
            return
        elif message.text.lower() == t3:
            mess = "The weather at " + t3 + ": \n" + methods.get_day_weather(3, data)
            self.bot.send_message(message.chat.id, mess, reply_markup=no_key_board)
            return
        elif message.text.lower() == t4:
            mess = "The weather at " + t4 + ": \n" + methods.get_day_weather(4, data)
            self.bot.send_message(message.chat.id, mess, reply_markup=no_key_board)
            return
        elif message.text.lower() == t5:
            mess = "The weather at " + t5 + ": \n" + methods.get_day_weather(5, data)
            self.bot.send_message(message.chat.id, mess, reply_markup=no_key_board)
            return
        # check for the command /wtime
        query = message.text.lower()
        for x in time_mess_array:
            if query.startswith(x):
                mes = query[14:]
                if mes == "at " + t1 or mes == "at " + t2 or mes == "at " + t3 or mes == "at " + t4 or mes == "at " + t5:
                    self.send_weather_at_time(message, reply_markup=no_key_board)
                    return
        # check if it was day message from command /wtime and make keyboakd for time query
        if query == "at " + t1 or query == "at " + t2 or query == "at " + t3 or query == "at " + t4 or query == "at " + t5:
            keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
            if int(message.text[3:5]) == today.day - 4:
                for x in time_mess_array:
                    if int(x[8:10]) > today.hour:
                        keyboard2.row(x + message.text, reply_markup=no_key_board)
            else:
                for x in time_mess_array:
                    keyboard2.row(x + message.text)
            self.bot.send_message(message.chat.id, "Choose time: ", reply_markup=keyboard2)
            return

        # send stiker to user if he print not command
        self.bot.send_sticker(message.chat.id, 'CAADAgADPgIAAkcVaAnaG0eZ4kbcKwI')
