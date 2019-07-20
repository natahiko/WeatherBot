import datetime


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


def get_weather_from_owm(w):
    today = datetime.datetime.now()
    weather_icon = get_weather_icon(w.get_weather_icon_name())
    wind_icon = get_wind_smiley(w.get_wind()['deg'])
    res = "({}.{}): \n{} {} ({})\n🌡 {}° {} {}m/s \nmin: {}° - max: {}° \nPresure: {}mm".format(today.day, today.month,
                                                                                                w.get_status(),
                                                                                                weather_icon,
                                                                                                w.get_detailed_status(),
                                                                                                int(round(
                                                                                                    w.get_temperature()[
                                                                                                        'temp'] - 273,
                                                                                                    15)),
                                                                                                wind_icon,
                                                                                                w.get_wind()['speed'],
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


def get_city_id(userid, mydb):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT cityid FROM users WHERE userid = {}".format(userid))
    myresult = mycursor.fetchall()[0]
    cityid = str(myresult)[1:(len(str(myresult)) - 2)]
    return int(cityid)


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


def get_help_text():
    res = "     /changecity - change the default city to have everyday weather in new place \n      " \
          "/now - to know weather at your default city in this moment \n       " \
          "/nowat [cityname] - to know weather in this moment in any city \n        " \
          "/today - to know weather for the rest of day \n     " \
          "/tomorrow - to know the weather for all day for tomorrow \n     " \
          "/wday - to know all day weather for next 5 day \n       " \
          "/wtime - to know the weather anytime for the one of next 5 day \n      " \
          "/help - to see the list of all command"
    return res;
