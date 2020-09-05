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

Install the dependencies (let the project root be `$PROJECT_ROOT`):

    cd $PROJECT_ROOT && pip install -r $PROJECT_ROOT/requirements.txt 

Set the needed [environment variables](#environment-variables).
You can also create a .env file at the root of the project and put them into it:

    touch $PROJECT_ROOT/.env

Run the provided script. You'll see a .session file to be created in the `$PROJECT_ROOT` folder:

    python $PROJECT_ROOT/bin/start_bot.py


# Environment variables

Get them from https://my.telegram.com

    TELEGRAM_API_ID
    TELEGRAM_API_HASH

Get it from https://telegram.me/botfather

    TELEGRAM_BOT_TOKEN  

Get it from https://mongodb.com

    MONGO_URL
    
Let it be anything you want

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

The entire bot has been coded in the the english language as my personal habitude.
However, since it was initially a private commitment, it has been designed to be used by Italians only.
Every text is written in the Italian language, every date is therefore converted in CET/CEST (it depends on DST).

Internationalization is not yet a priority, but any help is welcome.


# Special thanks

To @gpicc, who agreed to make it open source


# License
Copyright (c) 2020 [Midblyte](https://github.com/Midblyte)

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
