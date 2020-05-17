import datetime


def get_weather_icon(icon):
    if icon == '01d' or icon == '01n': return u'\U00002600'
    if icon == '02d' or icon == '02n': return u'\U000026C5'
    if icon == '03d' or icon == '03n': return u'\U00002601'
    if icon == '04d' or icon == '04n': return u'\U0001F32C'
    if icon == '09d' or icon == '09n': return u'\U0001F327'
    if icon == '10d' or icon == '10n': return u'\U0001F326'
    if icon == '11d' or icon == '11n': return u'\U000026C8'
    if icon == '13d' or icon == '13n': return u'\U00002744'
    if icon == '50d' or icon == '50n': return u'\U0001F32B'


def get_wind_smiley(deg):
    if deg > 350 or deg < 10: return u'\U000027A1'
    if deg > 80 and deg < 100: return u'\U00002B06'
    if deg > 170 and deg < 190: return u'\U00002B05'
    if deg > 260 and deg < 280: return u'\U00002B07'
    if deg > 10 and deg < 80: return u'\U00002197'
    if deg > 100 and deg < 170: return u'\U00002196'
    if deg > 190 and deg < 260: return u'\U00002199'
    if deg > 280 and deg < 350: return u'\U00002198'


# get text of weather in current time
def get_weather_from_owm(w):
    today = datetime.datetime.now()
    weather_icon = get_weather_icon(w.get_weather_icon_name())
    try:
        wind_icon = get_wind_smiley(w.get_wind()['deg'])
    except:
        print('this city hasnt argument deg')
        wind_icon = '🌬'
    res = "({}.{}): \n{} {} ({})\nu'\U0001F321' {}° {} {}m/s \nmin: {}° - max: {}° \nPresure: {}mm".format(today.day,
                                                                                                           today.month,
                                                                                                           w.get_status(),
                                                                                                           weather_icon,
                                                                                                           w.get_detailed_status(),
                                                                                                           int(round(
                                                                                                               w.get_temperature()[
                                                                                                                   'temp'] - 273,
                                                                                                               15)),
                                                                                                           wind_icon,
                                                                                                           w.get_wind()[
                                                                                                               'speed'],
                                                                                                           int(round(
                                                                                                               w.get_temperature()[
                                                                                                                   'temp_min'] - 273,
                                                                                                               15)),
                                                                                                           int(round(
                                                                                                               w.get_temperature()[
                                                                                                                   'temp_max'] - 273,
                                                                                                               15)),
                                                                                                           w.get_pressure()[
                                                                                                               'press'] * 0.75)
    return res


# get cityid by userid from db
def get_city_id(userid, mydb):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT cityid FROM users WHERE userid = {}".format(userid))
    try:
        myresult = mycursor.fetchall()[0]
        cityid = str(myresult)[1:(len(str(myresult)) - 2)]
        return int(cityid)
    except Exception as e:
        return 0


# get message text for all day from hour to hour
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
        w = [x][0]
        if hour < 10: result += '0'
        result += str(hour) + ":00: {} {} ({})\n     u'\U0001F321' {}° {} {}m/s \n".format(w['weather'][0]['main'],
                                                                                           get_weather_icon(
                                                                                               w['weather'][0]['icon']),
                                                                                           w['weather'][0][
                                                                                               'description'],
                                                                                           int(round(
                                                                                               w['main']['temp'] - 273,
                                                                                               15)),
                                                                                           get_wind_smiley(
                                                                                               w['wind']['deg']),
                                                                                           w['wind']['speed'])
        hour += 3
    return result


# the text of hepl message
def get_help_text():
    res = "/changecity - change the default city to have everyday weather in new place \n" \
          "/now - to know weather at your default city in this moment \n" \
          "/nowat [cityname] - to know weather in this moment in any city \n" \
          "/today - to know weather for the rest of day \n" \
          "/tomorrow - to know the weather for all day for tomorrow \n" \
          "/wday - to know all day weather for next 5 day \n" \
          "/wtime - to know the weather anytime for the one of next 5 day \n" \
          "/help - to see the list of all command"
    return res;
