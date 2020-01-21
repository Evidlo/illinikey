import base64
import json
import os
import sys
import requests
import pyotp
import re


CONFIG_PATH = os.path.expanduser('~/.cache/illinikey.json')
COUNTER_PATH = os.path.expanduser('~/.cache/illinikey_counter.json')

__license__ = "WTFPL"
__author__ = "Evan Widloski, Elnard Utiushev"


def getActivationData(code):
    print("Requesting activation data...")

    HEADERS = {
        "User-Agent": "okhttp/3.11.0",
    }

    PARAMS = {
        "app_id": "com.duosecurity.duomobile.app.DMApplication",
        "app_version": "2.3.3",
        "app_build_number": "323206",
        "full_disk_encryption": False,
        "manufacturer": "Google",
        "model": "Pixel",
        "platform": "Android",
        "jailbroken": False,
        "version": "6.0",
        "language": "EN",
        "customer_protocol": 1
    }

    ENDPOINT = "https://api-cd3ecedb.duosecurity.com/push/v2/activation/{}"

    res = requests.post(
        ENDPOINT.format(code),
        headers=HEADERS,
        params=PARAMS
    )

    if res.json().get('code') == 40403:
        print("Invalid activation code."
              "Please request a new activation link.")
        sys.exit(1)

    if not res.json()['response']:
        print("Unknown error")
        print(res.json())
        sys.exit(1)

    return res.json()['response']


def validateLink(link):
    try:
        assert "api-cd3ecedb.duosecurity.com" in link
        url_pattern = 'qr\?value=duo%3A%2F%2F(.+)-.+$'
        match = re.search(url_pattern, link)
        assert match is not None and len(match.groups()) == 1
        return True, match.groups()[0]
    except AssertionError:
        return False, None


def createConfig(activationData):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(activationData, f, indent=2)
    print("Activation data saved!")


def getConfig():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def setCounter(number):
    with open(COUNTER_PATH, 'w') as f:
        json.dump({
            "counter": number
        }, f, indent=2)


def getCounter():
    with open(COUNTER_PATH, 'r') as f:
        return json.load(f)['counter']


def generatePassword():
    config = getConfig()
    counter = getCounter()

    hotp = pyotp.HOTP(base64.b32encode(config['hotp_secret'].encode()))

    hotpPassword = hotp.at(counter)

    if config.get('pin'):
        password = "{},{}".format(config.get('pin'), hotpPassword)
    else:
        password = hotpPassword

    setCounter(counter + 1)

    return password


def askForInfo():
    print(
"""
1. Visit verify.uillinois.edu/manage and 'Add a new device'.
   > "Add a new device"
   > "Smartphone"
   > Continue
   > Enter a fake phone number or reuse your existing one
   > "Yes" you want to use the Duo Mobile App.
   > Continue (and replace existing number if asked)
   > "Android"
   > Continue
   > "I have Duo mobile installed" (no need to actually do this)
2. Right click on QR code, copy link to image and paste here
"""
    )

    valid = False
    while not valid:
        link = input('Activation link: ')
        valid, activationCode = validateLink(link)

        if not valid:
            print("Invalid link. Please try again")

    activationData = getActivationData(activationCode)
    activationData['pin'] = ''
    createConfig(activationData)
    setCounter(0)
    print(
        """
Setup successful!
illinikey can now generate offline keys that can be used on the Duo login page.
You can bind the following command to a keyboard shortcut for easy entry.

    sh -c 'xdotooltype $(illinikey)'
        """
    )


def main():
    if not os.path.isfile(CONFIG_PATH) or not os.path.isfile(COUNTER_PATH):
        print("Configuration files not found! Running setup...")
        askForInfo()
    else:
        print(generatePassword(), end='')


if __name__ == '__main__':
    main()
