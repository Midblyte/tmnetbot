tmnetbot - share your telegram channel by allowing other people to post into it through a bot

- [Setup and run](#setup-and-run)
- [Environment Variables](#environment-variables)
- [Description](#description)
- [Requirements](#requirements)
- [Limitations](#limitations)
- [Special thanks](#special-thanks)
- [License](#license)


# Setup and run

First, clone this repository. Type:

    git clone https://github.com/Midblyte/tmnetbot

Install the dependencies (let the project root be `tmnetbot`):

    cd tmnetbot && pip install -r requirements.txt 

Set the needed [environment variables](#environment-variables).
You can also create a .env file at the root of the project and put them into it:

    touch .env

Run the provided script. You'll see a .session file to be created in the folder:

    ./bin/start_bot.py  # OR  python ./bin/start_bot.py


# Environment variables

Get them from https://my.telegram.com

    TELEGRAM_API_ID
    TELEGRAM_API_HASH

Get it from https://telegram.me/botfather

    TELEGRAM_BOT_TOKEN  

Get it from https://mongodb.com

    MONGO_URL
    
Let it be anything you want (optional, defaults to `tmnetbot`)

    NETWORK_SHORT_NAME

###### The correct format of the .env file is `KEY = VALUE`. For each variable give it its own line.


# Description

**tmnetbot** is a Telegram bot.
It allows your users to forward messages from their channel into yours.
Useful for Telegram networks which do have a "best posts of the network" channel.
- Can handle waiting threshold, so admins of the same channel can't flood.
- Allows to set time ranges for when to send your messages, both for the network and the users. 


# Requirements

- It has been tested on Python 3.8.2, but should work for every Python 3.6+ version.
- Also, check out the requirements.txt file.
- Everything else you need has been previously specified in the [environment variables](#environment-variables) section.


# Limitations

The entire bot has been coded in the the english language as my personal habit.
However, since it was initially a private commitment, it has been designed to be used by Italians only.
Every text is written in the Italian language, every date is therefore converted in CET/CEST (it depends on DST).

Internationalization is not yet a priority, but any help is welcome.


# Special thanks

To @gpicc, who agreed to make it open source


# License
Copyright (C) 2020 [Midblyte](https://github.com/Midblyte)

Licensed under the terms of the [GNU General Public License v3 or later (GPLv3+)](https://github.com/Midblyte/tmnetbot/blob/master/LICENSE)
