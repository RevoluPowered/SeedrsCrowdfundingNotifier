import time
from lxml import html
import requests
from decimal import Decimal
from playsound import playsound
from pyttsx3 import init

site_url = 'https://www.seedrs.com/yatter'
reload_time = 10


def get_seedrs_profile():
    page = requests.get(site_url)
    return html.fromstring(page.content)


def get_investment_percentage( profile ):
    return str(profile.xpath('//div[@class="CampaignProgress-percentage"]/text()')).strip()


def get_investment_count( profile ):
    return str(profile.xpath('//span[@class="total"]/text()')).strip()


def get_current_investment_amount( profile ):
    amount = str(profile.xpath('//dl[@class="investment_already_funded"]/dd/text()')[0]).strip().replace(',', '')
    # convert to number
    return Decimal(amount[1:])


Engine = init()
# store initial percentage
InvestmentPercentage = get_investment_percentage(get_seedrs_profile())

print("amount: ", get_current_investment_amount(get_seedrs_profile()))


# debugging makes the alert run on startup
Debugging = True
InvestmentAmount = get_current_investment_amount(get_seedrs_profile())


def request_investment_info():
    global InvestmentPercentage
    global InvestmentAmount
    global Engine
    seedrs = get_seedrs_profile()
    current_percentage = get_investment_percentage(seedrs)

    if current_percentage != InvestmentPercentage or Debugging:
        investment_amount = get_current_investment_amount(seedrs)
        received_amount = investment_amount - InvestmentAmount
        #playsound('Action Stations.mp3')
        Engine.say('Investment amount received: £' + str(received_amount)+ ".")
        Engine.say('Investment percentage is now: ' + str(InvestmentPercentage) + ".")
        Engine.say('We now have: ' + get_investment_count(seedrs) + ' investors.')
        Engine.say('Our investment capital is now: £' + str(investment_amount))
        Engine.runAndWait()
        InvestmentPercentage = current_percentage


while True:
    request_investment_info()
    time.sleep(10)
