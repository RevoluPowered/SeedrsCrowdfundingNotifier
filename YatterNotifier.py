import time
from lxml import html
import requests
from decimal import Decimal
from playsound import playsound
from pyttsx3 import init
from plyer import notification
import json
import os
from pathlib import Path
from collections import namedtuple
from multiprocessing import Queue

app_dir = os.getcwd()

# check for config file
cfg_path = Path("config.json")

# Config globals
Config = dict()



def load_config():
    """ load configuration file, if one doesn't exist create it"""
    global Config
    if cfg_path.is_file():
        with open('config.json', encoding='utf-8') as json_data_file:
            Config = json.load(json_data_file)
    else:
        with open('config.json', 'w', encoding='utf-8') as json_data_file:

            config_new = {
                'seedrs_url': 'https://www.seedrs.com/yatter',
                'reload_time': 300,
                'play_sound': False,
                'show_notification': True
            }

            json.dump(config_new, json_data_file, sort_keys=True, indent=4)
            Config = config_new

load_config()




def get_seedrs_profile():
    global Config
    page = requests.get(Config['seedrs_url'])
    return html.fromstring(page.content)


def get_investment_percentage( profile ):
    return str(profile.xpath('//div[@class="CampaignProgress-percentage"]/text()')[0]).strip()


def get_investment_count( profile ):
    return str(profile.xpath('//span[@class="total"]/text()')[0]).strip()


def get_current_investment_amount( profile ):
    amount = str(profile.xpath('//dl[@class="investment_already_funded"]/dd/text()')[0]).strip().replace(',', '')
    # convert to number
    return Decimal(amount[1:])


Engine = init()
# store initial percentage
InvestmentPercentage = get_investment_percentage(get_seedrs_profile())

print("amount: ", get_current_investment_amount(get_seedrs_profile()))


# debugging makes the alert run on startup and ignores trigger case
Debugging = False
InvestmentAmount = get_current_investment_amount(get_seedrs_profile())


def request_investment_info():
    global InvestmentPercentage
    global InvestmentAmount
    global Engine
    global Config
    seedrs = get_seedrs_profile()
    current_percentage = get_investment_percentage(seedrs)

    if current_percentage != InvestmentPercentage or Debugging:
        investment_amount = get_current_investment_amount(seedrs)
        received_amount = investment_amount - InvestmentAmount
        #

        # is configuration enabled for playing text to speech notification
        if Config['play_sound']:
            playsound('notification_sound.mp3')
            Engine.say('Investment amount received: £' + str(received_amount)+ ".")
            Engine.say('Investment percentage is now: ' + str(InvestmentPercentage) + ".")
            Engine.say('We now have: ' + get_investment_count(seedrs) + ' investors.')
            Engine.say('Our investment capital is now: £' + str(investment_amount))

        # are the desktop notifications working
        if Config['show_notification']:
            notification.notify(
                title='Seedrs New Investment Received',
                message='Investment amount received £' + str(received_amount) + ", you're now " + str(InvestmentPercentage) + " percent funded. " + " Investment capital: £"+ str(investment_amount),
                app_name='Investment',
                app_icon='notification.ico'
            )



        Engine.runAndWait()
        InvestmentPercentage = current_percentage


while True:
    request_investment_info()
    time.sleep(Config['reload_time'])
