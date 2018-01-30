import sched, time
from lxml import html
import requests
from decimal import Decimal
from playsound import playsound
import pyttsx3
from plyer import notification
import json
import os
from pathlib import Path
from logging import basicConfig,  info, DEBUG
from collections import namedtuple
from multiprocessing import Queue

basicConfig(filename='polling.log', level=DEBUG)

Engine = pyttsx3.init(debug=True)

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

# store initial percentage
InvestorCountDelta = get_investment_count(get_seedrs_profile())

print("Initial amount: ", get_current_investment_amount(get_seedrs_profile()))


# debugging makes the alert run on startup and ignores trigger case
Debugging = False
InvestmentAmount = get_current_investment_amount(get_seedrs_profile())


def request_investment_info():
    global InvestorCountDelta
    global InvestmentAmount
    global Engine
    global Config
    seedrs = get_seedrs_profile()
    current_investor_count = get_investment_count(seedrs)
    info("Current investor count: " + current_investor_count)
    info("Previous investor count: " + InvestorCountDelta)
    if current_investor_count != InvestorCountDelta or Debugging:
        # Update investor count
        InvestorCountDelta = current_investor_count
        # Retrieve investment amount
        investment_amount = get_current_investment_amount(seedrs)
        # Work out investment amount
        received_amount = investment_amount - InvestmentAmount

        info("Investment amount changed")
        # is configuration enabled for playing text to speech notification
        if Config['play_sound']:
            playsound('notification_sound.mp3')
            Engine.say('Investment amount received: £' + str(received_amount)+ ".")
            Engine.say('Investment percentage is now: ' + str(InvestorCountDelta) + ".")
            Engine.say('We now have: ' + get_investment_count(seedrs) + ' investors.')
            Engine.say('Our investment capital is now: £' + str(investment_amount))

        # are the desktop notifications working
        if Config['show_notification']:
            # execute notification
            notification.notify(
                title='Seedrs New Investment Received',
                message='Investment amount received £' + str(received_amount) + ", you're now " + str(InvestorCountDelta) + " percent funded. " + " Investment capital: £" + str(investment_amount),
                app_name='Investment',
                app_icon='notification.ico'
            )

        Engine.runAndWait()



PollingInterval = float(Config['reload_time'])

s = sched.scheduler(time.time, time.sleep)
def investment_update(sc):
    info("polling for investment changes")
    request_investment_info()
    s.enter(PollingInterval, 1, investment_update, (sc,))

s.enter(PollingInterval, 1, investment_update, (s,))
s.run()


