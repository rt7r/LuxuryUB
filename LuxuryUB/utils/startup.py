import time
import asyncio
import glob
import os
import sys
from telethon.errors.rpcerrorlist import ChannelPrivateError
import urllib.request
from datetime import timedelta
from pathlib import Path
import requests
from telethon import Button, functions, types, utils
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import FloodWaitError
from LuxuryUB import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from ..Config import Config
from aiohttp import web
from ..core import web_server
from ..core.logger import logging
from ..core.session import luxur
# جلب الدوال من مكانها الصحيح
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)

LOGS = logging.getLogger("Luxury")

async def setup_bot():
    try:
        await luxur.connect()
        bot_details = await luxur.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", Config.PORT).start()
        
        luxur.me = await luxur.get_me()
        luxur.uid = luxur.tgbot.uid = utils.get_peer_id(luxur.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(luxur.me)
    except Exception as e:
        LOGS.error(f"Error in setup: {str(e)}")
        sys.exit()

async def startupmessage():
    if not BOTLOG: return
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
            message = await luxur.get_messages(msg_details[0], ids=msg_details[1])
            await luxur.edit_message(msg_details[0], msg_details[1], message.text + "\n\n**᯽︙ تم تشغيل لوكجوري بنجاح ✓**")
            # ✅ التعديل: إضافة OWNER_ID لـ gvarstatus
            if gvarstatus(Config.OWNER_ID, "restartupdate") is not None:
                await luxur.send_message(msg_details[0], ".بنك", reply_to=msg_details[1], schedule=timedelta(seconds=10))
            del_keyword_collectionlist("restart_update")
    except Exception as e: LOGS.error(e)

async def mybot():
    try:
        starkbot = await luxur.tgbot.get_me()
        if starkbot.bot_inline_placeholder:
            print("ForEver") # هذي اللي تطلع عندك باللوج
        else:
            await luxur.send_message("@BotFather", "/setinline")
            await asyncio.sleep(1)
            await luxur.send_message("@BotFather", f"@{starkbot.username}")
            await asyncio.sleep(1)
            await luxur.send_message("@BotFather", "لوكجوري 💎")
    except Exception as e: print(e)

async def verifyLoggerGroup():
    """هذا هو المكان اللي جان يسبب الخطأ الكارثي"""
    flag = False
    if not BOTLOG:
        botlog_group_id = await luxury_is_best(luxur, "مجموعة الأشعارات")
        if botlog_group_id:
            # ✅ التعديل: إضافة OWNER_ID لـ addgvar
            addgvar(Config.OWNER_ID, "PRIVATE_GROUP_BOT_API_ID", botlog_group_id)
        else:
            from .tools import create_supergroup
            _, groupid = await create_supergroup("مجموعة اشعارات لوكــجوري", luxur, Config.TG_BOT_USERNAME, "مجموعة الإشعارات", None)
            addgvar(Config.OWNER_ID, "PRIVATE_GROUP_BOT_API_ID", groupid)
        flag = True

    if PM_LOGGER_GROUP_ID == -100:
        pm_logger_group_id = await luxury_is_best(luxur, "مجموعة التخزين")
        if pm_logger_group_id:
            addgvar(Config.OWNER_ID, "PM_LOGGER_GROUP_ID", pm_logger_group_id)
        else:
            from .tools import create_supergroup
            _, groupid = await create_supergroup("مجموعة التخزين لوكـجوري", luxur, Config.TG_BOT_USERNAME, "مجموعة التخزين", None)
            addgvar(Config.OWNER_ID, "PM_LOGGER_GROUP_ID", groupid)
        flag = True
    
    if flag:
        # إعادة تشغيل لتثبيت الفارات
        os.execl(sys.executable, sys.executable, "-m", "LuxuryUB")

async def luxury_is_best(luxur, group_name):
    async for dialog in luxur.iter_dialogs():
        if dialog.is_group and dialog.title == group_name: return dialog.id
    return None

async def load_plugins(folder):
    from .pluginmanager import load_module
    path = f"LuxuryUB/{folder}/*.py"
    files = glob.glob(path)
    for name in files:
        try:
            pluginname = Path(name).stem
            load_module(pluginname, plugin_path=f"LuxuryUB/{folder}")
        except Exception as e: LOGS.info(f"Fail: {e}")

async def add_bot_to_logger_group(chat_id):
    bot_details = await luxur.tgbot.get_me()
    try:
        await luxur(functions.channels.InviteToChannelRequest(channel=chat_id, users=[bot_details.username]))
    except Exception: pass