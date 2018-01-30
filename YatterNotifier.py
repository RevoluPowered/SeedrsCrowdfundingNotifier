import sched, time
from lxml import html
from collections import namedtuple
from multiprocessing import Queue
from functools import wraps
import requests
from plyer import notification as osnotify
from decimal import Decimal
from playsound import playsound
from pathlib import Path
from logging import basicConfig, info, DEBUG
from queue import Queue
import pyttsx3
import json
import os
import pystray
from threading import Thread
from PIL import Image

basicConfig(filename='polling.log', level=DEBUG)

Engine = None



def InitSpeechEngine():
    global Engine
    for attempt in range(10):
        try:
            info("activate speech service")
            Engine = pyttsx3.init(debug=False)
            time.sleep(1.0)
        except:
            info("activate speech service, stage one")
        else:
            info("Successfully connected locally to speech service")
            break
    # we failed all the attempts - deal with the consequences.


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
                'show_notification': True,
                'text_to_speech': True,
                'debugging_enabled': False
            }

            json.dump(config_new, json_data_file, sort_keys=True, indent=4)
            Config = config_new


load_config()

Debugging = Config['debugging_enabled']


def get_seedrs_profile():
    global Config
    page = requests.get(Config['seedrs_url'])
    return html.fromstring(page.content)


def get_investment_percentage(profile):
    return str(profile.xpath('//div[@class="CampaignProgress-percentage"]/text()')[0]).strip()


def get_investment_count(profile):
    return str(profile.xpath('//span[@class="total"]/text()')[0]).strip()


def get_current_investment_amount(profile):
    amount = str(profile.xpath('//dl[@class="investment_already_funded"]/dd/text()')[0]).strip().replace(',', '')
    # convert to number
    return Decimal(amount[1:])


# store initial percentage
InvestorCountDelta = get_investment_count(get_seedrs_profile())

print("Initial amount: ", get_current_investment_amount(get_seedrs_profile()))

# debugging makes the alert run on startup and ignores trigger case

InvestmentAmount = get_current_investment_amount(get_seedrs_profile())


def request_investment_info():
    global InvestorCountDelta
    global InvestmentAmount
    # global Engine
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
        investment_percentage = get_investment_percentage(seedrs)
        # Work out investment amount
        received_amount = investment_amount - InvestmentAmount
        info("Investment amount changed")

        # do we want notify sounds?
        if Config['play_sound']:
            playsound('notification_sound.mp3')

        # are the desktop notifications working
        if Config['show_notification']:
            # execute notification
            osnotify.notify(
                title='Seedrs New Investment Received',
                message='Investment amount received £' + str(received_amount) + ", you're now " + str(
                    investment_percentage) + " percent funded. " + " Investment capital: £" + str(investment_amount),
                app_name='Investment',
                app_icon='notification.ico'
            )

        # is configuration enabled for playing text to speech notification
        if Config['text_to_speech']:
            Engine.say('Investment amount received: £' + str(received_amount) + ".")
            Engine.say('Investment percentage is now: ' + str(investment_percentage) + ".")
            Engine.say('We now have: ' + get_investment_count(seedrs) + ' investors.')
            Engine.say('Our investment capital is now: £' + str(investment_amount))
            Engine.runAndWait()


PollingInterval = float(Config['reload_time'])

if Config['text_to_speech']:
    InitSpeechEngine()

osnotify.notify(
    title='Seedrs Notifications Activated',
    message='Monitoring ' + str(Config['seedrs_url']) + ' for any changes, every ' + str(PollingInterval) + " seconds.",
    app_name='Investment',
    app_icon='notification.ico'
)


def investment_polling(queue):
    info("executing work on separate thread")
    s = sched.scheduler(time.time, time.sleep)

    def investment_update(sc):
        info("polling for investment changes")
        request_investment_info()
        data = queue.get()
        if data != "exit":
            s.enter(PollingInterval, 1, investment_update, (sc,))

    # wait 5 seconds before running first poll
    s.enter(5, 1, investment_update, (s,))
    s.run()


def ui_updates(queue):
    info("executing work for UI information")

    def get_image_icon():
        return Image.open("notification.ico")

    icon_taskbar = pystray.Icon(
        'Seedrs Notification Tool',
        title="Seedrs Notification Tool"
    )

    icon_taskbar.icon = get_image_icon()

    def exit():
        """ exit application thread"""
        icon_taskbar.stop()
        queue.put("exit")

    def configure_icon(icon):
        icon.visible = True
        item = pystray.MenuItem("Exit", exit)
        icon.menu = pystray.Menu(item)

    icon_taskbar.run(configure_icon)


event_queue = Queue()

threads = []
work_thread = Thread(target=investment_polling, args=(event_queue,))
threads.append(work_thread)

ui_thread = Thread(target=ui_updates, args=(event_queue,))
threads.append(ui_thread)

# start worker and ui
for thread in threads:
    thread.start()

# join thread
for thread in threads:
    thread.join()

# ui_runner = threads[1]
# when this thread exits the other will be forced to exit too
# ui_runner.join()
