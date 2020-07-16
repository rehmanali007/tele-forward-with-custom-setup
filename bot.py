#!/usr/bin/python

from telethon import TelegramClient, events, errors
from telethon.events import StopPropagation
from configparser import ConfigParser
import json
import socks
import re
# import logging


config = ConfigParser()
config.read('conf.ini')


# logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
# level=logging.WARNING)

api_id = config['TELEGRAM']['api_id']
api_hash = config['TELEGRAM']['api_hash']
target_group = config['TELEGRAM'].getint('telegram_destination_group_id')
session_file = 'telegramBot'


sent_msgs = 0
# ##############################################< Proxy >##############################################

try:
    proxy_enabled = config['PROXY'].getboolean('enable')
    proxy_server = config['PROXY']['server'].encode()
    proxy_port = config['PROXY'].getint('port')
except KeyError:
    proxy_enabled = True
    proxy_server = '159.89.49.60'
    proxy_port = 31264
    pass


# if config['proxy']['enable']:
#     sockProxy = {
#         "proxy_type": socks.SOCKS5,
#         "addr": conf.SOCKS5_SERVER,
#         "port": conf.SOCKS5_PORT,
#         "rdns": True,
#         "username": conf.USERNAME,
#         "password": conf.PASSWORD
#     }


if proxy_enabled:
    # print(f'Using proxy server {proxy_server}:{proxy_port}')
    telegramClient = TelegramClient(session_file, api_id, api_hash, proxy=(
        socks.SOCKS5, proxy_server, proxy_port))
else:
    telegramClient = TelegramClient(session_file, api_id, api_hash)

dest_channel = config['TELEGRAM'].getint('destination_channel')
chats = json.loads(config.get("TELEGRAM", "source_channels"))
filtered_channels = json.loads(config.get("TELEGRAM", "filtered_channels"))


def deEmojify(text):
    # A python function to remove emojis from string
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


@telegramClient.on(events.NewMessage(chats, blacklist_chats=False))
async def newMessageHandler(msg):
    await telegramClient.send_message(dest_channel, msg.message)
    global sent_msgs
    sent_msgs += 1
    print(f'[+] Forwarded Messages: {sent_msgs}', end='\r')
    raise StopPropagation


@telegramClient.on(events.NewMessage(chats=filtered_channels, blacklist_chats=False))
async def filteredMessageHandler(msg):
    global num_of_msgs
    if msg.message.media:
        raise StopPropagation
    emojiFiltered = deEmojify(msg.message.message)
    await telegramClient.send_message(dest_channel, emojiFiltered)
    global sent_msgs
    sent_msgs += 1
    print(f'[+] Forwarded Messages: {sent_msgs}', end='\r')
    raise StopPropagation


try:
    telegramClient.start(phone='+923089442289')
    print("-------------------------\nMessage Forward bot is up!\n-------------------------\n")
    telegramClient.run_until_disconnected()
except KeyboardInterrupt:
    print("[+] Quiting bot!")
except errors.rpcerrorlist.ApiIdInvalidError:
    print("[+] Invalid API_ID/API_HASH")
