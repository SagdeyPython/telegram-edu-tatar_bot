# encoding: utf - 8
import os
import pickle
import traceback
from functools import wraps
import pyowm
import telegram
from selenium import webdriver
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater
import sqlite3
from dotenv import load_dotenv
path_env = r"C:\Users\Руслан\PycharmProjects\\teleBot\\telegram-edu-tatar_bot\.env"
load_dotenv(dotenv_path=path_env)
token = os.getenv("TOKEN")

author = {
    'Алгебра': {
        '9': {
            'Ю.Н. Макарычев, Н.Г. Миндюк': 'makarichev-14',
        },
        '10-11': {
            'Ш.А. Алимов, Ю.М. Колягин': 'alimov-15',
        },
        '8': {
            'Ю.Н. Макарычев, Н.Г. Миндюк': 'makarychev-8',
        },
        '7': {
            'Ю.Н. Макарычев, Н.Г. Миндюк(Углуб.)': 'makarychev-uglublennoe-izuchenie',
        },
    }
}

con = sqlite3.connect("gdz.db")
cursor = con.cursor()
chrome_options = webdriver.ChromeOptions()
hostname = '193.233.78.155'
port = '65233'
#chrome_options.add_argument('--proxy-server=%s' % hostname + ":" + port)
chrome_options.add_argument('--proxy-server=http://bbildroid:S3n1ZiQ@193.233.78.155:65233') # --proxy-server=http://bbildroid:S3n1ZiQ@193.233.78.155:65233
chromedriver_path = 'chromedriver.exe'
owm = pyowm.OWM(token, language='ru')
import zipfile

PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(chromedriver_path))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        chrome_options=chrome_options)
    return driver

class_people = ''
subject = {
    'Алгебра': 'algebra',
    'Английский': 'english',
    'Биология': 'biologiya',
    'История': 'istoriya',
    'География': 'geografiya',
    'Геометрия': 'geometria',
    'Информатика и ИКТ': 'informatika',
    'Литература': 'geografiya',
    'Обществознание': 'obshhestvoznanie',
    'ОБЖ': 'obshhestvoznanie',
    'Физика': 'fizika',
    'Химия': 'himiya',
    'Русский': 'russkii_yazik'
}
bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
chats_file = 'chats.txt'
data_file = 'data.txt'
domashka = {}
ex_table = {}
chats = pickle.load(open(chats_file, 'rb')) if os.path.exists(chats_file) else {}
f = open(data_file, 'r')
if len(f.read()) > 0:
    data = pickle.load(open(data_file, 'rb')) if os.path.exists(chats_file) else {}
else:
    data = {'12': '12'}
f.close()
print(bot.get_me())
print(data)
glavnoe_menu_keyboard = [['Настройка', 'Домашка на завтра'],
                         ['Информация', 'Получить ГДЗ']]
textbook_menu_keyboard = [['Алгебра', 'Геометрия'], ['Русский'], ['Назад в главное меню']]
algebra_textbooks = [['Ю.Н. Макарычев, Н.Г. Миндюк', 'А.Г. Мерзляк, В.Б. Полонский'], ['Ш.А. Алимов, Ю.М. Колягин'],
                     ['Назад в главное меню', 'Назад в меню выбора учебников']]
russki_textbooks = [['Тростенцова Л.А., Ладыженская Т.А.', 'С.Г. Бархударов, С.Е. Крючков'],
                    ['М.М. Разумовская, С.И. Львова'], ['Назад в главное меню', 'Назад в меню выбора учебников']]
geometriya_textbooks = [['Л.С. Атанасян, В.Ф. Бутузов', 'А.В. Погорелов'], ['Ершова A.П., Голобородько B.В.'],
                        ['Назад в главное меню', 'Назад в меню выбора учебников']]


def found_ex_in_dz(ex_for_gdz):
    exp_more = []
    exp = ''
    ex_for_gdz = ex_for_gdz.lower()
    if 'упр' in ex_for_gdz:
        position = ex_for_gdz.rindex('упр') + 2
        if len(ex_for_gdz) - 1 > position + 1:
            if ex_for_gdz[position + 1] == '.':
                if len(ex_for_gdz) - 1 > position + 2:
                    if ex_for_gdz[position + 2] == ' ':
                        if ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4] == '-':
                                for i in range(int(ex_for_gdz[position + 3]),
                                               int(ex_for_gdz[position + 5]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 5] == '-':
                                exp += ex_for_gdz[position + 4]
                                for i in range(int(exp), int(
                                        ex_for_gdz[position + 6] + ex_for_gdz[position + 7]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if ex_for_gdz[position + 6] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 7] + ex_for_gdz[position + 8] +
                                                ex_for_gdz[
                                                    position + 9]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 4].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 5].isdigit():
                                            exp += ex_for_gdz[position + 5]
                    else:
                        if ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3] == '-':
                                for i in range(int(ex_for_gdz[position + 2]),
                                               int(ex_for_gdz[position + 4]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4] == '-':
                                exp += ex_for_gdz[position + 3]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 5] + ex_for_gdz[
                                                   position + 6]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if ex_for_gdz[position + 5] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                                ex_for_gdz[
                                                    position + 8]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 4:
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 5:
                                        if ex_for_gdz[position + 3].isdigit():
                                            exp += ex_for_gdz[position + 4]
            elif ex_for_gdz[position + 1] == ' ':
                if ex_for_gdz[position + 1] == ' ':
                    if ex_for_gdz[position + 2].isdigit():
                        exp += ex_for_gdz[position + 2]
                        if ex_for_gdz[position + 3] == '-':
                            for i in range(int(ex_for_gdz[position + 2]),
                                           int(ex_for_gdz[position + 4]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 4] == '-':
                            exp += ex_for_gdz[position + 3]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 5] + ex_for_gdz[
                                               position + 6]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                            ex_for_gdz[
                                                position + 8]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 5:
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if len(ex_for_gdz) - 1 > position + 6:
                                    if ex_for_gdz[position + 4].isdigit():
                                        exp += ex_for_gdz[position + 4]
                else:
                    if ex_for_gdz[position + 3] == ' ':
                        if ex_for_gdz[position + 4].isdigit():
                            exp += ex_for_gdz[position + 4]
                            if len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 6].isdigit():
                                            exp += ex_for_gdz[position + 6]
            else:
                if ex_for_gdz[position + 1].isdigit():
                    if ex_for_gdz[position + 1].isdigit():
                        exp += ex_for_gdz[position + 1]
                        if ex_for_gdz[position + 2] == '-':
                            for i in range(int(ex_for_gdz[position + 1]),
                                           int(ex_for_gdz[position + 3]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3] == '-':
                            exp += ex_for_gdz[position + 2]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 4] + ex_for_gdz[
                                               position + 5]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 4] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 5] + ex_for_gdz[position + 6] +
                                            ex_for_gdz[
                                                position + 7]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 4:
                            if ex_for_gdz[position + 2].isdigit():
                                exp += ex_for_gdz[position + 2]
                                if len(ex_for_gdz) - 1 > position + 5:
                                    if ex_for_gdz[position + 3].isdigit():
                                        exp += ex_for_gdz[position + 2]
    elif '№№' in ex_for_gdz:
        position = ex_for_gdz.rindex('№№') + 1
        if len(ex_for_gdz) - 1 > position + 1:
            if ex_for_gdz[position + 1] == '.':
                if len(ex_for_gdz) - 1 > position + 2:
                    if ex_for_gdz[position + 2] == ' ':
                        if ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4] == '-':
                                for i in range(int(ex_for_gdz[position + 3]),
                                               int(ex_for_gdz[position + 5]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 5] == '-':
                                exp += ex_for_gdz[position + 4]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 6] + ex_for_gdz[
                                                   position + 7]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if ex_for_gdz[position + 6] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 7] + ex_for_gdz[position + 8] +
                                                ex_for_gdz[
                                                    position + 9]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 4].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 5].isdigit():
                                            exp += ex_for_gdz[position + 5]
                    else:
                        if ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3] == '-':
                                for i in range(int(ex_for_gdz[position + 2]),
                                               int(ex_for_gdz[position + 4]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4] == '-':
                                exp += ex_for_gdz[position + 3]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 5] + ex_for_gdz[
                                                   position + 6]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if ex_for_gdz[position + 5] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                                ex_for_gdz[
                                                    position + 8]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 4:
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 5:
                                        if ex_for_gdz[position + 3].isdigit():
                                            exp += ex_for_gdz[position + 4]
            elif ex_for_gdz[position + 1] == ' ':
                if ex_for_gdz[position + 1] == ' ':
                    if ex_for_gdz[position + 2].isdigit():
                        exp += ex_for_gdz[position + 2]
                        if ex_for_gdz[position + 3] == '-':
                            for i in range(int(ex_for_gdz[position + 2]),
                                           int(ex_for_gdz[position + 4]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 4] == '-':
                            exp += ex_for_gdz[position + 3]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 5] + ex_for_gdz[
                                               position + 6]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                            ex_for_gdz[
                                                position + 8]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 5:
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if len(ex_for_gdz) - 1 > position + 6:
                                    if ex_for_gdz[position + 4].isdigit():
                                        exp += ex_for_gdz[position + 4]
                else:
                    if ex_for_gdz[position + 3] == ' ':
                        if ex_for_gdz[position + 4].isdigit():
                            exp += ex_for_gdz[position + 4]
                            if len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 6].isdigit():
                                            exp += ex_for_gdz[position + 6]
            else:
                if ex_for_gdz[position + 1].isdigit():
                    if ex_for_gdz[position + 1].isdigit():
                        exp += ex_for_gdz[position + 1]
                        if ex_for_gdz[position + 2] == '-':
                            for i in range(int(ex_for_gdz[position + 1]),
                                           int(ex_for_gdz[position + 3]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3] == '-':
                            exp += ex_for_gdz[position + 2]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 4] + ex_for_gdz[
                                               position + 5]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 4] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 5] + ex_for_gdz[position + 6] +
                                            ex_for_gdz[
                                                position + 7]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 4:
                            if ex_for_gdz[position + 2].isdigit():
                                exp += ex_for_gdz[position + 2]
                                if len(ex_for_gdz) - 1 > position + 5:
                                    if ex_for_gdz[position + 3].isdigit():
                                        exp += ex_for_gdz[position + 2]
    elif '№' in ex_for_gdz:
        position = ex_for_gdz.rindex('№')
        if len(ex_for_gdz) - 1 > position + 1:
            if ex_for_gdz[position + 1] == '.':
                if len(ex_for_gdz) - 1 > position + 2:
                    if ex_for_gdz[position + 2] == ' ':
                        if ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4] == '-':
                                for i in range(int(ex_for_gdz[position + 3]),
                                               int(ex_for_gdz[position + 5]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 5] == '-':
                                exp += ex_for_gdz[position + 4]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 6] + ex_for_gdz[
                                                   position + 7]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if ex_for_gdz[position + 6] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 7] + ex_for_gdz[position + 8] + ex_for_gdz[
                                                    position + 9]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 4].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 5].isdigit():
                                            exp += ex_for_gdz[position + 5]
                    else:
                        if ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3] == '-':
                                for i in range(int(ex_for_gdz[position + 2]),
                                               int(ex_for_gdz[position + 4]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4] == '-':
                                exp += ex_for_gdz[position + 3]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 5] + ex_for_gdz[
                                                   position + 6]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if ex_for_gdz[position + 5] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                                ex_for_gdz[
                                                    position + 8]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 4:
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 5:
                                        if ex_for_gdz[position + 3].isdigit():
                                            exp += ex_for_gdz[position + 4]
            elif ex_for_gdz[position + 1] == ' ':
                if ex_for_gdz[position + 1] == ' ':
                    if ex_for_gdz[position + 2].isdigit():
                        exp += ex_for_gdz[position + 2]
                        if ex_for_gdz[position + 3] == '-':
                            for i in range(int(ex_for_gdz[position + 2]),
                                           int(ex_for_gdz[position + 4]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 4] == '-':
                            exp += ex_for_gdz[position + 3]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 5] + ex_for_gdz[
                                               position + 6]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                            ex_for_gdz[
                                                position + 8]) + 1):
                                                    exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 5:
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if len(ex_for_gdz) - 1 > position + 6:
                                    if ex_for_gdz[position + 4].isdigit():
                                        exp += ex_for_gdz[position + 4]
                else:
                    if ex_for_gdz[position + 3] == ' ':
                        if ex_for_gdz[position + 4].isdigit():
                            exp += ex_for_gdz[position + 4]
                            if len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 6].isdigit():
                                            exp += ex_for_gdz[position + 6]
            else:
                if ex_for_gdz[position + 1].isdigit():
                    if ex_for_gdz[position + 1].isdigit():
                        exp += ex_for_gdz[position + 1]
                        if ex_for_gdz[position + 2] == '-':
                            for i in range(int(ex_for_gdz[position + 1]),
                                           int(ex_for_gdz[position + 3]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3] == '-':
                            exp += ex_for_gdz[position + 2]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 4] + ex_for_gdz[
                                               position + 5]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 4] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 5] + ex_for_gdz[position + 6] +
                                            ex_for_gdz[
                                                position + 7]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 4:
                            if ex_for_gdz[position + 2].isdigit():
                                exp += ex_for_gdz[position + 2]
                                if len(ex_for_gdz) - 1 > position + 5:
                                    if ex_for_gdz[position + 3].isdigit():
                                        exp += ex_for_gdz[position + 2]
    elif 'параграф' in ex_for_gdz:
        position = ex_for_gdz.rindex('параграф') + 7
        if len(ex_for_gdz) - 1 > position + 1:
            if ex_for_gdz[position + 1] == '.':
                if len(ex_for_gdz) - 1 > position + 2:
                    if ex_for_gdz[position + 2] == ' ':
                        if ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4] == '-':
                                for i in range(int(ex_for_gdz[position + 3]),
                                               int(ex_for_gdz[position + 5]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 5] == '-':
                                exp += ex_for_gdz[position + 4]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 6] + ex_for_gdz[
                                                   position + 7]) + 1):
                                                        exp_more.append(i)
                            elif ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if ex_for_gdz[position + 6] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 7] + ex_for_gdz[position + 8] +
                                                ex_for_gdz[
                                                    position + 9]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 4].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 5].isdigit():
                                            exp += ex_for_gdz[position + 5]
                    else:
                        if ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3] == '-':
                                for i in range(int(ex_for_gdz[position + 2]),
                                               int(ex_for_gdz[position + 4]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 4] == '-':
                                exp += ex_for_gdz[position + 3]
                                for i in range(int(exp),
                                               int(ex_for_gdz[position + 5] + ex_for_gdz[
                                                   position + 6]) + 1):
                                    exp_more.append(i)
                            elif ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 4]
                                    if ex_for_gdz[position + 5] == '-':
                                        for i in range(int(exp), int(
                                                ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                                ex_for_gdz[
                                                    position + 8]) + 1):
                                            exp_more.append(i)
                            elif len(ex_for_gdz) - 1 > position + 4:
                                if ex_for_gdz[position + 3].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 5:
                                        if ex_for_gdz[position + 3].isdigit():
                                            exp += ex_for_gdz[position + 4]
            elif ex_for_gdz[position + 1] == ' ':
                if ex_for_gdz[position + 1] == ' ':
                    if ex_for_gdz[position + 2].isdigit():
                        exp += ex_for_gdz[position + 2]
                        if ex_for_gdz[position + 3] == '-':
                            for i in range(int(ex_for_gdz[position + 2]),
                                           int(ex_for_gdz[position + 4]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 4] == '-':
                            exp += ex_for_gdz[position + 3]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 5] + ex_for_gdz[
                                               position + 6]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3].isdigit():
                            exp += ex_for_gdz[position + 3]
                            if ex_for_gdz[position + 4].isdigit():
                                exp += ex_for_gdz[position + 4]
                                if ex_for_gdz[position + 5] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 6] + ex_for_gdz[position + 7] +
                                            ex_for_gdz[
                                                position + 8]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 5:
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if len(ex_for_gdz) - 1 > position + 6:
                                    if ex_for_gdz[position + 4].isdigit():
                                        exp += ex_for_gdz[position + 4]
                else:
                    if ex_for_gdz[position + 3] == ' ':
                        if ex_for_gdz[position + 4].isdigit():
                            exp += ex_for_gdz[position + 4]
                            if len(ex_for_gdz) - 1 > position + 5:
                                if ex_for_gdz[position + 5].isdigit():
                                    exp += ex_for_gdz[position + 5]
                                    if len(ex_for_gdz) - 1 > position + 6:
                                        if ex_for_gdz[position + 6].isdigit():
                                            exp += ex_for_gdz[position + 6]
            else:
                if ex_for_gdz[position + 1].isdigit():
                    if ex_for_gdz[position + 1].isdigit():
                        exp += ex_for_gdz[position + 1]
                        if ex_for_gdz[position + 2] == '-':
                            for i in range(int(ex_for_gdz[position + 1]),
                                           int(ex_for_gdz[position + 3]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 3] == '-':
                            exp += ex_for_gdz[position + 2]
                            for i in range(int(exp),
                                           int(ex_for_gdz[position + 4] + ex_for_gdz[
                                               position + 5]) + 1):
                                exp_more.append(i)
                        elif ex_for_gdz[position + 2].isdigit():
                            exp += ex_for_gdz[position + 2]
                            if ex_for_gdz[position + 3].isdigit():
                                exp += ex_for_gdz[position + 3]
                                if ex_for_gdz[position + 4] == '-':
                                    for i in range(int(exp), int(
                                            ex_for_gdz[position + 5] + ex_for_gdz[position + 6] +
                                            ex_for_gdz[
                                                position + 7]) + 1):
                                        exp_more.append(i)
                        elif len(ex_for_gdz) - 1 > position + 4:
                            if ex_for_gdz[position + 2].isdigit():
                                exp += ex_for_gdz[position + 2]
                                if len(ex_for_gdz) - 1 > position + 5:
                                    if ex_for_gdz[position + 3].isdigit():
                                        exp += ex_for_gdz[position + 2]
    if len(exp_more) == 0:
        exp_more.append(exp)
    return exp_more

def send_everyone(text, silent=False):
    for chat_id in chats:
        bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True,
                         disable_notification=silent)


def get_homework(login, password):
    driver = get_chromedriver(use_proxy=True)
    global learning, class_people, domashka, ex_table
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

    for s in day_subjects:
        sub = ''
        if len(s[2].split()) > 2:
            for i in range(1, len(s[2].split())):
                sub += s[2].split()[i]
                sub += ' '
                sub.rstrip()
        else:
                sub += s[2].split()[1]
        sub.rstrip()
        domashka[sub] = (s[3] if len(s) == 4 else '')
        ex_table[sub] = found_ex_in_dz((s[3] if len(s) == 4 else ''))

    for s in day_subjects:
        domashka[f"{s[2].split(' ')[1]}"] = (s[3] if len(s) == 4 else '')
    day_subjects = [
        s[0] + s[1] + s[2].split(' ')[0] + ' | ' + s[2].split(' ')[1] + (' | ' + s[3] if len(s) == 4 else '')
        for s in day_subjects]
    learning = [i.split(' | ')[-1] if len(i.split(' | ')) == 2 else i.split(' | ')[-2] for i in day_subjects]
    homework = '\n'.join(day_subjects)

    driver.get('https://edu.tatar.ru/user/diary/week')
    panel = driver.find_element_by_class_name('top-panel-user')
    full_name_or_class = panel.find_element_by_tag_name('span')
    full_name_or_class_text = full_name_or_class.text
    class_people = full_name_or_class_text.split()[-2]
    class_people = class_people[:-1]

    driver.quit()

    return homework


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
    with open(chats_file, 'wb') as file:
        pickle.dump(chats, file)
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Я бот ГДЗ")


def default_test(update, custom_keyboard, text):
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=text,
                     reply_markup=reply_markup)


@catch_error
def textbook_mode(update, context):
    text = update.message.text
    algebra_flag_have_textbook = False
    for i in algebra_textbooks:
        for j in i:
            if text == j:
                algebra_flag_have_textbook = True
    geometriya_flag_have_textbook = False
    for i in geometriya_textbooks:
        for j in i:
            if text == j:
                geometriya_flag_have_textbook = True
    russki_flag_have_textbook = False
    for i in russki_textbooks:
        for j in i:
            if text == j:
                russki_flag_have_textbook = True
    if 'Алгебра' in text:
        default_test(update, algebra_textbooks, '~Режим выбора учебника по алгебре~\n'
                                                'Выберите автора учебника')
    elif 'Геометрия' in text:
        default_test(update, geometriya_textbooks, '~Режим выбора учебника по алгебре~\n'
                                                   'Выберите автора учебника')
    elif 'Русский' in text:
        default_test(update, russki_textbooks, '~Режим выбора учебника по русскому~\n'
                                               'Выберите автора учебника')
    elif 'Назад в главное меню' in text:
        dispatcher.remove_handler(textbook_handler)
        dispatcher.add_handler(text_handler)
        default_test(update, glavnoe_menu_keyboard, 'Получение меню')
    elif 'Назад в меню выбора учебников' in text:
        default_test(update, textbook_menu_keyboard, 'Возвращение в меню выбора учебников')
    elif algebra_flag_have_textbook:
        print(update.message.text)
        data[f"{update.message.chat_id} algebra"] = f"{text}"
        with open(data_file, 'wb') as file:
            pickle.dump(data, file)
        context.bot.send_message(chat_id=update.message.chat_id, text='Успешно введено')
    elif geometriya_flag_have_textbook:
        print(update.message.text)
        data[f"{update.message.chat_id} geometriya"] = f"{text}"
        with open(data_file, 'wb') as file:
            pickle.dump(data, file)
        context.bot.send_message(chat_id=update.message.chat_id, text='Успешно введено')
    elif russki_flag_have_textbook:
        print(update.message.text)
        data[f"{update.message.chat_id} russki"] = f"{text}"
        with open(data_file, 'wb') as file:
            pickle.dump(data, file)
        context.bot.send_message(chat_id=update.message.chat_id, text='Успешно введено')


@catch_error
def text(update, context):
    text = update.message.text
    global learning, class_people, subject, domashka, author, ex_table
    found_author_sub = ''
    subject_day = []
    for i in subject_day:
        if i in text:
            predmdet = i
            break
    if text == 'Помощь':
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Чем тебе помочь?")
    elif text.lower().startswith('всем: '):
        send_everyone(f'Пользователь {update.message.chat_id} передаёт всем: {text[6:]}', silent=True)
    elif 'Посмотреть учебники' in text:
        print(data)
    elif '123' in text:
        custom_keyboard = [['Настройка', 'Домашка на завтра'],
                           ['Информация', 'Получить ГДЗ']]
        default_test(update, custom_keyboard, 'Получение меню')
    elif 'Домашка на завтра' in text:
        if not data[f'{update.message.chat_id} + log'] or not data[f'{update.message.chat_id} + pass']:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="Не удалось получить ДЗ. Введите логин и пароль в поле \"Вход\"")
            return 0
        custom_keyboard = [['Вход', 'Домашка на завтра'],
                           ['Информация', 'Получить ГДЗ']]
        default_test(update, custom_keyboard, 'Получение домашки')
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"""ДЗ на завтра: {get_homework(login=data[f'{update.message.chat_id} + log'],
                                                                    password=data[
                                                                        f'{update.message.chat_id} + pass'])}""")
    elif 'Получить ГДЗ' in text:
        if len(domashka) > 0:
            custom_keyboard = []
            for i in domashka.keys():
                if not ('Физическая' in i or 'Родной' in i or 'Иностран' in i):
                    custom_keyboard.append([i])
            default_test(update, custom_keyboard, 'Выберите предмет')
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="Для начала получите домашку \"Домашка на завтра\"")
    elif 'Алгебра' in text:
        context.bot.send_message(chat_id=update.message.chat_id,
                                      text='Напишите свой учебник, или выберите из этих - ')
        custom_keyboard = [[i] for i in author['Алгебра'][class_people].keys()]
        default_test(update, custom_keyboard, 'Меню учебников')
    elif text in author['Алгебра'][class_people].keys():
        for i in ex_table['Алгебра']:
            site = r"https://gdz.ru/class-" + class_people + "/algebra/" + \
                   author['Алгебра'][class_people][text] + "/" + i + "-nom/"
            driver = webdriver.Chrome(chromedriver_path)
            driver.get(site)
            images = driver.find_elements_by_tag_name('img')
            # for image in images:
            #    print(image.get_attribute('src'))
            product_img = driver.find_element_by_class_name('with-overtask')
            # product_img = driver.find_element_by_css_selector("img[alt='']")
            # print(product_img)
            product_img = product_img.find_element_by_tag_name('img')
            img = product_img.get_attribute('src')
            bot.send_photo(chat_id=update.message.chat_id, photo=img)
            driver.quit()
    elif 'Настройка' in text:
        custom_keyboard = [['Вход'], ['Режим выбора учебников']]
        default_test(update, custom_keyboard, 'Меню настройки')
    elif 'Режим выбора учебников' in text:
        default_test(update, textbook_menu_keyboard, 'ВНИМЕНИЕ\n'
                                                     'ПЕРЕХОД В РЕЖИМ ВЫБОРА УЧЕБНИКОВ')
        dispatcher.remove_handler(text_handler)
        dispatcher.add_handler(textbook_handler)
    elif 'Вход' in text:
        context.bot.send_message(chat_id=update.message.chat_id, text=(f"Для ввода данных пишите:\n"
                                                                       "\'Данные ЛОГИН ПАРОЛЬ\'\n"
                                                                       'Где ЛОГИН - ваш логин в edu.tatar.tu\n'
                                                                       'А ПАРОЛЬ - ваш пароль\n'
                                                                       ))
    elif 'Данные' in text:
        _, login, password = text.split(' ')
        data[f"{update.message.chat_id} + log"] = f"{login}"
        data[f"{update.message.chat_id} + pass"] = f"{password}"
        with open(data_file, 'wb') as file:
            pickle.dump(data, file)
        context.bot.send_message(chat_id=update.message.chat_id, text='Успешно введено')
    elif 'Информация' in text:
        context.bot.send_message(chat_id=update.message.chat_id, text='Info')

    elif text.lower().startswith('решение'):  # 'решение\n def solution()'
        solution_start = text.find('\n') + 1
        solution_code = text[solution_start:]
        print(solution_code)
    elif text.lower().startswith('дз'):
        _, login, password = text.split(' ')
        context.bot.send_message(chat_id=update.message.chat_id, text=f"ДЗ на завтра: {get_homework(login, password)}")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=(f"Нет команды: {update.message.text}.\n"
                                                                       "Есть:\n"
                                                                       '1."Всем: [сообщение]"\n'
                                                                       '2."ДЗ [логин] [пароль]"\n'
                                                                       ))


textbook_handler = MessageHandler(Filters.text, textbook_mode)
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

text_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(text_handler)
updater.start_polling()