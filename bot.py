#encoding: utf - 8
import os
import pickle
import traceback
from functools import wraps

import pyowm
import telegram
from selenium import webdriver
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater

chromedriver_path = '~/chromedriver'
owm = pyowm.OWM('6d00d1d4e704068d70191bad2673e0cc', language='ru')
token = '966099929:AAFvO0r7vBMobeINw-Ve86FdD80WXagNVaM'
if not token:
    raise ValueError('966099929:AAFvO0r7vBMobeINw-Ve86FdD80WXagNVaM')

bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
chats_file = 'chats.txt'
chats = set()
print(bot.get_me())


def send_everyone(text, silent=False):
    for chat_id in chats:
        bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True,
                         disable_notification=silent)


def get_homework(login, password):
    driver = webdriver.Chrome(chromedriver_path)

    driver.get('https://edu.tatar.ru/logon')

    login_input = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[2]/form/div[4]/input[1]')
    login_input.send_keys(login)

    pass_input = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[2]/form/div[4]/input[2]')
    pass_input.send_keys(password)

    login_buttom = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[2]/form/div[4]/div/button')
    login_buttom.click()

    driver.get('https://edu.tatar.ru/user/diary/day')

    next_day_button = driver.find_element_by_xpath(
        '//*[@id="content"]/div[2]/div/div/div[2]/table/tbody/tr/td[3]/span/a')
    next_day_button.click()

    day_table = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div/div/div[3]/table/tbody')

    day_subjects = day_table.find_elements_by_tag_name('tr')
    day_subjects = [subject.text.split('\n') for subject in day_subjects]
    day_subjects = [
        s[0] + s[1] + s[2].split(' ')[0] + ' | ' + s[2].split(' ')[1] + (' | ' + s[3] if len(s) == 4 else '')
        for s in day_subjects]

    homework = '\n'.join(day_subjects)

    driver.quit()

    return homework


def get_weather(observation):
    w = observation.get_weather()
    status, temp = w.get_detailed_status(), w.get_temperature(unit='celsius')['temp']
    return status + temp

def test_solution(function):
    def ord_rus(letter):
        if letter <= 'е':
            return ord(letter) - ord('а') + 1
        elif letter == 'ё':
            return ord('е') + 1 - ord('а') + 1
        else:
            return ord(letter) - ord('а') + 2

    tests = {
        'кок': 16,
        'лёд': 15,
        'мама': 0,
        'банан': 2,
        'контрольная': 57,
        'выходи': 22,
        'решать': 5,
    }

    result = []
    for word, v in tests.items():
        if function(word) != v:
            result.append(f'{word} == {[ord_rus(l) for l in word]}: {function(word)} != {v}')
    result.append(function('программирование'))
    return '\n'.join(result)


def catch_error(f):
    @wraps(f)
    def wrap(update, context):
        try:
            return f(update, context)
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id, text="Error occured: " + traceback.format_exc())

    return wrap


@catch_error
def start(update, context):
    print('received', update.message.chat_id)
    chats.add(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Я бот IT JUMP")


@catch_error
def text(update, context):
    text = update.message.text
    if text == 'Помощь':
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Чем тебе помочь?")
    elif text.lower().startswith('всем: '):
        send_everyone(f'Пользователь {update.message.chat_id} передаёт всем: {text[6:]}', silent=True)
    elif text.lower().startswith('решение'):  # 'решение\n def solution()'
        solution_start = text.find('\n') + 1
        solution_code = text[solution_start:]
        print(solution_code)
    elif text.lower().startswith('дз'):
        _, login, password = text.split(' ')
        context.bot.send_message(chat_id=update.message.chat_id, text=f"ДЗ на завтра: {get_homework(login, password)}")
    elif text.lower().startswith('погода '):
        location = text[7:]
        weather = owm.weather_at_place(location)
        weather_text = get_weather(weather)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Погода в {location}: {weather_text}")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=(f"Нет команды: {update.message.text}.\n"
                                                                       "Есть:\n"
                                                                       '1."Всем: [сообщение]"\n'
                                                                       '2."погода [город]"\n'
                                                                       '3."ДЗ [логин] [пароль]"\n'
                                                                       '4."решение\\n[def solution(word):..]")'
                                                                       '5.Отправка локации для погоды\n'
                                                                       ))


@catch_error
def location(update, context):
    longitude, latitude = update.message.location['longitude'], update.message.location['latitude']
    weather = owm.weather_at_coords(latitude, longitude)
    weather_text = get_weather(weather)
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Погода в {longitude} {latitude}: {weather_text}")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

text_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(text_handler)

location_handler = MessageHandler(Filters.location, location)
dispatcher.add_handler(location_handler)

updater.start_polling()
