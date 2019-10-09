"""
Description:
    The background process to communicate with the arduino, CSH LDAP,
    and the front end GUI. This includes the LDAP classes and the Thread
    that is run from the front end to deal with all the communication.
    The thread takes input from the arduino to update LDAP and the GUI.
Author:
    JD <jd@csh.rit.edu>
"""

from datetime import datetime
import time
import os
import requests

drink_url = None
money_log = None
session = requests.Session()

def init(money_log_name, api_key):
    """
    Used to set the configurations needed to work
    """
    global drink_url
    global money_log
    global session
    drink_url = 'https://drink.csh.rit.edu/'
    session.headers = {
        'X-Auth-Token': api_key
        'Content-Type': 'application/json'
    }
    money_log = money_log_name


def logging(errorMessage, e=None):
    """
    Logs all messages to include both error messages and normal info messages.
        All logs are placed in logs/<date>.log so everyday has its own file
    Parameters:
        errorMessage: the message to report
        e: the stacktrack if aviable for the error message
    """
    timeStamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    day = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
    file_name = "logs/" + day + ".log"
    if not os.path.exists("logs"):
        os.makedirs("logs/")
    f = open(file_name, "a")

    f.write(timeStamp + ": " + errorMessage + "\n")
    print(errorMessage, e)
    if not e == None:
        f.write("\t" + str(e) + "\n")
    f.close()

def user_info(ibutton):
    """
    Gets the information about a user given their ibutton
    """
    response = session.get(drink_url % 'users/credits' + "&ibutton=%s" % ibutton)
    print(response.text)
    print(response.json)
    response = response.json()
    print("\niButton present. getting json\n")
    try:
        return (response['user']['uid'],
            int(response['user']['drinkBalance'])
    except Exception as e:
        print(e)

def increment_credits(uid, credits):
    """
    Updates the given user's drink credits and returns the user's new credits
    """
    data = {'uid': uid, 'drinkBalance': credits}
    response = requests.post(drink_url % 'users/credits', data = data).json()
    logging(str(response))
    try:
        with open(money_log, 'r') as f:
            money_in_machine = int(f.read())
        with open(money_log, 'w') as f:
            f.write(str(money_in_machine + credits))
    except Exception as e:
        logging(str(e))
        with open(money_log, 'w') as f:
            f.write(str(credits))
    return int(response['data'])

def money_in_machine():
    try:
        with open(money_log, 'r') as f:
            return float(f.read())
    except Exception as e:
        reset_money_log()
        return 0

def reset_money_log():
    with open(money_log, 'w') as f:
        f.write('0')
