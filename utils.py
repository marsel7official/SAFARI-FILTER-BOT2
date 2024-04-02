import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, ChatAdminRequired
from info import *
from imdb import Cinemagoer 
import asyncio
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import enums
from typing import Union
from Script import script
import pytz
import random 
from asyncio import sleep
import time
import re
import os
from datetime import datetime, timedelta, date, time
import string
from typing import List
from database.users_chats_db import db
from bs4 import BeautifulSoup
import requests
import aiohttp
from shortzy import Shortzy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
	@@ -29,10 +30,11 @@
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = Cinemagoer()
TOKENS = {}
VERIFIED = {}
BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)
	@@ -47,23 +49,16 @@ class temp(object):
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}
    VERIFY = {}
    SEND_ALL_TEMP = {}
    KEYWORD = {}
    BOT = None
    JK_DEV = {}
    SHORT = {}
    GETALL = {}
    SPELL_CHECK = {}


async def is_subscribed(bot, query=None, userid=None):
    try:
        if userid == None and query != None:
            user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
        else:
            user = await bot.get_chat_member(AUTH_CHANNEL, int(userid))
    except UserNotParticipant:
        pass
    except Exception as e:
	@@ -163,18 +158,32 @@ async def broadcast_messages(user_id, message):
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Rᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ Dᴀᴛᴀʙᴀsᴇ, sɪɴᴄᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Bʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PᴇᴇʀIᴅIɴᴠᴀʟɪᴅ")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
	@@ -212,13 +221,9 @@ def get_size(size):
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def get_file_id(msg: Message):
    if msg.media:
	@@ -456,41 +461,6 @@ def humanbytes(size):
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

async def get_tutorial(chat_id):
    settings = await get_settings(chat_id) #fetching settings for group
    if 'tutorial' in settings.keys():
        if settings['is_tutorial']:
            TUTORIAL_URL = settings['tutorial']
        else:
            TUTORIAL_URL = TUTORIAL
    else:
        TUTORIAL_URL = TUTORIAL
    return TUTORIAL_URL

async def get_verify_shorted_link(link):
    API = SHORTLINK_API
    URL = SHORTLINK_URL
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)

    if URL == "api.shareus.in":
        url = f"https://{URL}/shortLink"
        params = {"token": API,
                  "format": "json",
                  "link": link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json(content_type="text/html")
                    if data["status"] == "success":
                        return data["shortlink"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/shortLink?token={API}&format=json&link={link}'

        except Exception as e:
            logger.error(e)
            return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
    else:
        url = f'https://{URL}/api'
        params = {'api': API,
                  'url': link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json()
                    if data["status"] == "success":
                        return data['shortenedUrl']
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/api?api={API}&link={link}'

        except Exception as e:
            logger.error(e)
            return f'{URL}/api?api={API}&link={link}'

async def get_users():
    count  = await user_col.count_documents({})
    cursor = user_col.find({})
    list   = await cursor.to_list(length=int(count))
    return count, list

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
	@@ -574,29 +594,27 @@ async def check_token(bot, userid, token):
    else:
        return False

async def get_token(bot, userid, link, fileid):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    url = f"{link}verify-{user.id}-{token}-{fileid}"
    status = await get_verify_status(user.id)
    date_var = status["date"]
    time_var = status["time"]
    hour, minute, second = time_var.split(":")
    year, month, day = date_var.split("-")
    last_date, last_time = str((datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second)))-timedelta(hours=24)).split(" ")
    tz = pytz.timezone('Asia/Kolkata')
    curr_date, curr_time = str(datetime.now(tz)).split(" ")
    if last_date == curr_date:
        vr_num = 2
    else:
        vr_num = 1
    shortened_verify_url = await get_verify_shorted_link(vr_num, url)
    return str(shortened_verify_url)

async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
	@@ -648,181 +666,114 @@ async def check_verification(bot, userid):
            return True
    else:
        return False

async def send_all(bot, userid, files, ident):
    if AUTH_CHANNEL and not await is_subscribed(bot=bot, userid=userid):
        try:
            invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Mᴀᴋᴇ sᴜʀᴇ Bᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ Fᴏʀᴄᴇsᴜʙ ᴄʜᴀɴɴᴇʟ")
            return
        if ident == 'filep' or 'checksubp':
            pre = 'checksubp'
        else:
            pre = 'checksub' 
        btn = [[
                InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Bᴀᴄᴋ-Uᴘ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)
            ],[
                InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#send_all")
            ]]
        await bot.send_message(
            chat_id=userid,
            text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴅᴏɴ'ᴛ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ...\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '❆ Jᴏɪɴ Oᴜʀ Bᴀᴄᴋ-Uᴘ Cʜᴀɴɴᴇʟ ❆' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ʙᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '↻ Tʀʏ Aɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...\n\nTʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇs...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return 'fsub'
    if await db.has_premium_access(userid):
        for file in files:
            f_caption = file.caption
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('@') and not x.startswith('www'), file.file_name.split()))
            size = get_size(file.file_size)
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                            file_size='' if size is None else size,
                                                            file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    print(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:

                await bot.send_cached_media(
                    chat_id=userid,
                    file_id=file.file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                            InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file.file_id}")
                        ],[
                            InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                            InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                            ]
                        ]
                    )
                )
            except UserIsBlocked:
                logger.error(f"Usᴇʀ: {userid} ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ!")
                return "Usᴇʀ ɪs ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ ! Uɴʙʟᴏᴄᴋ ᴛᴏ sᴇɴᴅ ғɪʟᴇs!"
            except PeerIdInvalid:
                logger.error("Eʀʀᴏʀ: Pᴇᴇʀ ID ɪɴᴠᴀʟɪᴅ !")
                return "Pᴇᴇʀ ID ɪɴᴠᴀʟɪᴅ !"
            except Exception as e:
                logger.error(f"Eʀʀᴏʀ: {e}")
                return f"Eʀʀᴏʀ: {e}"
        return 'jk_dev'
    if IS_VERIFY and not await check_verification(bot, userid):
        btn = [[
            InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(bot, userid, f"https://telegram.me/{temp.U_NAME}?start=", 'send_all')),
            InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ],[
            InlineKeyboardButton("💸 𝐑𝐞𝐦𝐨𝐯𝐞 𝐕𝐞𝐫𝐢𝐟𝐲 💸", callback_data='seeplans')
        ]]
        await bot.send_message(
            chat_id=userid,
            text=(script.VERIFY_TEXT),
            protect_content=True if PROTECT_CONTENT else False,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return 'verify'
    for file in files:
        f_caption = file.caption
        title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('@') and not x.startswith('www'), file.file_name.split()))
        size = get_size(file.file_size)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                        file_size='' if size is None else size,
                                                        file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                print(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        try:

            await bot.send_cached_media(
                chat_id=userid,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=True if ident == "filep" else False,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                        InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file.file_id}")
                    ],[
                        InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                        InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                        ]
                    ]
                )
            )
        except UserIsBlocked:
            logger.error(f"Usᴇʀ: {userid} ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ!")
            return "Usᴇʀ ɪs ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ ! Uɴʙʟᴏᴄᴋ ᴛᴏ sᴇɴᴅ ғɪʟᴇs!"
        except PeerIdInvalid:
            logger.error("Eʀʀᴏʀ: Pᴇᴇʀ ID ɪɴᴠᴀʟɪᴅ !")
            return "Pᴇᴇʀ ID ɪɴᴠᴀʟɪᴅ !"
        except Exception as e:
            logger.error(f"Eʀʀᴏʀ: {e}")
            return f"Eʀʀᴏʀ: {e}"
    return 'done'

async def get_verify_status(userid):
    status = temp.VERIFY.get(userid)
    if not status:
        status = await db.get_verified(userid)
        temp.VERIFY[userid] = status
    return status

async def update_verify_status(userid, date_temp, time_temp):
    status = await get_verify_status(userid)
    status["date"] = date_temp
    status["time"] = time_temp
    temp.VERIFY[userid] = status
    await db.update_verification(userid, date_temp, time_temp)

async def verify_user(bot, userid, token):
    user = await bot.get_users(int(userid))
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    date_var = datetime.now(tz)+timedelta(hours=12)
    temp_time = date_var.strftime("%H:%M:%S")
    date_var, time_var = str(date_var).split(" ")
    await update_verify_status(user.id, date_var, temp_time)

async def check_verification(bot, userid):
    user = await bot.get_users(int(userid))
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    curr_time = now.strftime("%H:%M:%S")
    hour1, minute1, second1 = curr_time.split(":")
    curr_time = time(int(hour1), int(minute1), int(second1))
    status = await get_verify_status(user.id)
    date_var = status["date"]
    time_var = status["time"]
    years, month, day = date_var.split('-')
    comp_date = date(int(years), int(month), int(day))
    hour, minute, second = time_var.split(":")
    comp_time = time(int(hour), int(minute), int(second))
    if comp_date<today:
        return False
    else:
        if comp_date == today:
            if comp_time<curr_time:
                return False
            else:
                return True
        else:
            return True
