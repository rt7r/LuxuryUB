import sys
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import LuxuryUB
from LuxuryUB import BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from .Config import Config
from .core.logger import logging
from .core.session import luxur 
from .helpers.utils.startup import (
    add_bot_to_logger_group,
    load_plugins,
    setup_bot,
    mybot,
    startupmessage,
    verifyLoggerGroup,
)
# استدعاء دالة جلب الحسابات الفرعية
from .sql_helper.global_collectionjson import get_collections

LOGS = logging.getLogger("Luxury")

async def start_internal_clients():
    """هذا هو الجزء المسؤول عن التشغيل المتعدد"""
    sub_sessions = get_collections(Config.OWNER_ID)
    if not sub_sessions:
        LOGS.info("ℹ️ لا توجد حسابات فرعية لتشغيلها.")
        return

    LOGS.info(f"🚀 جاري تشغيل {len(sub_sessions)} حساب فرعي...")
    for sess in sub_sessions:
        data = sess.json
        try:
            # إنشاء عميل جديد لكل جلسة فرعية
            client = TelegramClient(StringSession(data.get("session")), Config.APP_ID, Config.API_HASH)
            await client.start(bot_token=data.get("token"))
            LOGS.info(f"✅ تم تشغيل حساب: {data.get('name')} بنجاح ✓")
        except Exception as e:
            LOGS.error(f"❌ فشل تشغيل حساب {data.get('name')}: {str(e)}")

async def startup_process():
    try:
        LOGS.info("💎 جارِ بدء سورس لوكجوري ✓")
        await setup_bot()
        await mybot()
        
        await verifyLoggerGroup()
        await load_plugins("plugins")
        await load_plugins("assistant")
        
        # 🔥 تشغيل الحسابات المتعددة
        await start_internal_clients()
        
        print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
        print("᯽︙ سـورس لـوكجـوري يعـمل بـنجاح ✓")
        print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
        
        await add_bot_to_logger_group(BOTLOG_CHATID)
        if PM_LOGGER_GROUP_ID != -100:
            await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
        await startupmessage()
    except Exception as e:
        LOGS.error(f"❌ خطأ كارثي: {str(e)}")
        sys.exit()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup_process())
    luxur.run_until_disconnected()