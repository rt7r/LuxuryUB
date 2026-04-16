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
from ..helpers.utils import install_pip
from ..helpers.utils.utils import runcmd
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

LOGS = logging.getLogger("Luxury")
logging.getLogger('telethon').setLevel(logging.WARNING)

cmdhr = Config.COMMAND_HAND_LER
bot = luxur
ENV = bool(os.environ.get("ENV", False))

if ENV:
    VPS_NOLOAD = ["سيرفر"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["هيروكو"]

async def setup_bot():
    """
    To set up bot for LuxuryUB
    """
    try:
        await luxur.connect()
        config = await luxur(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == luxur.session.server_address:
                if luxur.session.dc_id != option.id:
                    LOGS.warning(
                        f"⌯︙معرف ثابت في الجلسة من {luxur.session.dc_id}"
                        f"⌯︙لـ  {option.id}"
                    )
                luxur.session.set_dc(option.id, option.ip_address, option.port)
                luxur.session.save()
                break
        bot_details = await luxur.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        luxuryport = Config.PORT
        await web.TCPSite(app, bind_address, luxuryport).start()
        luxur.me = await luxur.get_me()
        luxur.uid = luxur.tgbot.uid = utils.get_peer_id(luxur.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(luxur.me)
    except Exception as e:
        LOGS.error(f"كـود تيرمكس - {str(e)}")
        sys.exit()

async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            Config.CATUBLOGO = await luxur.tgbot.send_file(
                BOTLOG_CHATID,
                "https://k.top4top.io/p_3757trgqt1.jpg",
                caption="**‏᯽︙ بــوت لـوكجـوري يـعـمـل بـنـجـاح ✓ \n᯽︙ أرسل `.الاوامر` لرؤية اوامر السورس \n  ᯽︙ المطور : @rt7r_2**",
                buttons=[(Button.url("سورس لوكجوري", "https://t.me/ee2en"),)],
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist(Config.OWNER_ID, "restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await luxur.check_testcases()
            message = await luxur.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**تم تشغيل البوت الأن أرسل `.فحص`**"
            await luxur.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus(Config.OWNER_ID, "restartupdate") is not None:
                await luxur.send_message(
                    msg_details[0],
                    f"{cmdhr}بنك",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            try:
                del_keyword_collectionlist(Config.OWNER_ID, "restart_update")
            except:
                pass 
    except Exception as e:
        LOGS.error(e)
        return None


async def mybot():
    try:
        starkbot = await luxur.tgbot.get_me()
        luxury_name = "لوكجوري 💎"
        bot_name = starkbot.first_name
        botname = f"@{starkbot.username}"
        if bot_name.endswith("Assistant"):
            print("تم تشغيل البوت")
        if starkbot.bot_inline_placeholder:
            print("ForEver")
        else:
            try:
                await luxur.send_message("@BotFather", "/setinline")
                await asyncio.sleep(1)
                await luxur.send_message("@BotFather", botname)
                await asyncio.sleep(1)
                await luxur.send_message("@BotFather", luxury_name)
                await asyncio.sleep(2)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await luxur.tgbot.get_me()
    try:
        await luxur(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await luxur(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))
                
async def load_plugins(folder, extfolder=None):
    """
    تحميل ملفات السورس
    """
    if extfolder:
        path = f"{extfolder}/*.py"
        plugin_path = extfolder
    else:
        path = f"LuxuryUB/{folder}/*.py"
        plugin_path = f"LuxuryUB/{folder}"
    files = glob.glob(path)
    files.sort()
    success = 0
    failure = []
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            pluginname = shortname.replace(".py", "")
            try:
                if (pluginname not in Config.NO_LOAD) and (
                    pluginname not in VPS_NOLOAD
                ):
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                pluginname,
                                plugin_path=plugin_path,
                            )
                            if shortname in failure:
                                failure.remove(shortname)
                            success += 1
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if shortname not in failure:
                                failure.append(shortname)
                            if check > 5:
                                break
                else:
                    os.remove(Path(f"{plugin_path}/{shortname}.py"))
            except Exception as e:
                if shortname not in failure:
                    failure.append(shortname)
                LOGS.info(f"لم يتم تحميل {shortname} بسبب خطأ {e}\nمسار الملف {plugin_path}")
    if extfolder:
        if not failure:
            failure.append("None")
        await luxur.tgbot.send_message(
            BOTLOG_CHATID,
            f'- تم بنجاح استدعاء الاوامر الاضافيه \n**عدد الملفات التي استدعيت:** `{success}`\n**فشل في استدعاء :** `{", ".join(failure)}`',
        )

# سورس لوكجوري عمك
async def luxury_the_best(luxur, group_name):
    async for dialog in luxur.iter_dialogs():
        if dialog.is_group and dialog.title == group_name:
            return dialog.id
    return None

async def verifyLoggerGroup():
    """
    Will verify both loggers group
    """
    flag = False
    if BOTLOG:
        try:
            entity = await luxur.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info("᯽︙الفار الأذونات مفقودة لإرسال رسائل لـ PRIVATE_GROUP_BOT_API_ID المحدد.")
                if entity.default_banned_rights.invite_users:
                    LOGS.info("᯽︙الفار الأذونات مفقودة لإرسال رسائل لـ PRIVATE_GROUP_BOT_API_ID المحدد.")
        except ValueError:
            LOGS.error("᯽︙تـأكد من فـار المجـموعة  PRIVATE_GROUP_BOT_API_ID.")
        except TypeError:
            LOGS.error("᯽︙لا يمكـن العثور على فار المجموعه PRIVATE_GROUP_BOT_API_ID. تأكد من صحتها.")
        except Exception as e:
            LOGS.error("᯽︙حدث استثناء عند محاولة التحقق من PRIVATE_GROUP_BOT_API_ID.\n" + str(e))
    else:
        descript = "- عزيزي المستخدم هذه هي مجموعه الاشعارات يرجى عدم حذفها "
        photo_path1 = "LuxuryUB/luxur/razan/resources/start/Luxury.jpg"
        photobt = await luxur.upload_file(file=photo_path1) if os.path.exists(photo_path1) else None
        
        # يبحث عن الكروب القديم قبل ما يسوي جديد
        botlog_group_id = await luxury_the_best(luxur, "مجموعة اشعارات لوكــجوري")
        if botlog_group_id:
            addgvar(Config.OWNER_ID, "PRIVATE_GROUP_BOT_API_ID", botlog_group_id)
            print("᯽︙تم العثور على مجموعة المساعدة بالفعل وإضافتها إلى المتغيرات.")
        else:
            _, groupid = await create_supergroup(
                "مجموعة اشعارات لوكــجوري", luxur, Config.TG_BOT_USERNAME, descript, photobt
            )
            addgvar(Config.OWNER_ID, "PRIVATE_GROUP_BOT_API_ID", groupid)
            print("᯽︙تم إنشاء مجموعة المسـاعدة بنجاح وإضافتها إلى المتغيرات.")
        flag = True
        
    if PM_LOGGER_GROUP_ID == -100:
        descript = "᯽︙ وظيفه الكروب يحفظ رسائل الخاص اذا ما تريد الامر احذف الكروب نهائي \n  "
        photo_path2 = "LuxuryUB/luxur/razan/resources/start/Luxury2.jpg"
        photobt2 = await luxur.upload_file(file=photo_path2) if os.path.exists(photo_path2) else None
        
        # يبحث عن الكروب القديم قبل ما يسوي جديد
        pm_logger_group_id = await luxury_the_best(luxur, "مجموعة التخزين لوكـجوري")
        if pm_logger_group_id:
            addgvar(Config.OWNER_ID, "PM_LOGGER_GROUP_ID", pm_logger_group_id)
            print("تـم العثور على مجموعة الكروب التخزين بالفعل واضافة الـفارات الـيها.")
        else:
            _, groupid = await create_supergroup(
                "مجموعة التخزين لوكـجوري", luxur, Config.TG_BOT_USERNAME, descript, photobt2
            )
            addgvar(Config.OWNER_ID, "PM_LOGGER_GROUP_ID", groupid)
            print("تـم عمـل الكروب التخزين بنـجاح واضافة الـفارات الـيه.")
        flag = True
        
    if flag:
        executable = sys.executable.replace(" ", "\\ ")
        args = [executable, "-m", "LuxuryUB"]
        os.execle(executable, *args, os.environ)
        sys.exit(0)

async def install_externalrepo(repo, branch, cfolder):
    luxuryREPO = repo
    rpath = os.path.join(cfolder, "requirements.txt")
    if luxuryBRANCH := branch:
        repourl = os.path.join(luxuryREPO, f"tree/{luxuryBRANCH}")
        gcmd = f"git clone -b {luxuryBRANCH} {luxuryREPO} {cfolder}"
        errtext = f"لا يوحد فرع بأسم `{luxuryBRANCH}` في الريبو الخارجي {luxuryREPO}. تاكد من اسم الفرع عبر فار (`EXTERNAL_REPO_BRANCH`)"
    else:
        repourl = luxuryREPO
        gcmd = f"git clone {luxuryREPO} {cfolder}"
        errtext = f"الرابط ({luxuryREPO}) الذي وضعته لفار `EXTERNAL_REPO` غير صحيح عليك وضع رابط صحيح"
    response = urllib.request.urlopen(repourl)
    if response.code != 200:
        LOGS.error(errtext)
        return await luxur.tgbot.send_message(BOTLOG_CHATID, errtext)
    await runcmd(gcmd)
    if not os.path.exists(cfolder):
        LOGS.error("هنالك خطأ اثناء استدعاء رابط الملفات الاضافية يجب التأكد من الرابط اولا ")
        return await luxur.tgbot.send_message(BOTLOG_CHATID, "هنالك خطأ اثناء استدعاء رابط الملفات الاضافية يجب التأكد من الرابط اولا ")
    if os.path.exists(rpath):
        await runcmd(f"pip3 install --no-cache-dir -r {rpath}")
    await load_plugins(folder="LuxuryUB", extfolder=cfolder)