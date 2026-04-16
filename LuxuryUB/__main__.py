import sys
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
import LuxuryUB
from LuxuryUB import BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from .Config import Config
from .core.logger import logging
from .core.session import luxur 
from .utils import (
    add_bot_to_logger_group,
    load_plugins,
    setup_bot,
    mybot,
    startupmessage,
    verifyLoggerGroup,
)
# استدعاء دالة جلب الجلسات من نظام الـ JSON المطور
from .sql_helper.global_collectionjson import get_collections

LOGS = logging.getLogger("Luxury")

print("💎 Luxury TEAM (C) 2024 - 2026")
print("Licensed under the terms of the Luxury Team License")

cmdhr = Config.COMMAND_HAND_LER

async def start_internal_clients():
    """تشغيل كافة الحسابات المنصبة داخلياً من قاعدة البيانات"""
    # جلب كل الجلسات التابعة للمالك الأساسي
    sub_sessions = get_collections(Config.OWNER_ID)
    
    if not sub_sessions:
        LOGS.info("ℹ️ لا توجد حسابات فرعية منصبة داخلياً.")
        return

    LOGS.info(f"🚀 جاري تشغيل {len(sub_sessions)} حساب منصب داخلياً...")
    
    for sess in sub_sessions:
        data = sess.json
        session_str = data.get("session")
        bot_token = data.get("token")
        name = data.get("name")
        
        try:
            # إنشاء عميل (Client) جديد لكل جلسة
            client = TelegramClient(StringSession(session_str), Config.APP_ID, Config.API_HASH)
            await client.start(bot_token=bot_token)
            LOGS.info(f"✅ تم تشغيل حساب: {name} بنجاح ✓")
        except Exception as e:
            LOGS.error(f"❌ فشل تشغيل حساب {name}: {str(e)}")

async def luxury_startup():
    try:
        LOGS.info("💎 جارِ بدء سورس لوكجوري - الحساب الرئيسي ✓")
        await setup_bot()
        await mybot()
    except Exception as e:
        LOGS.error(f"❌ خطأ في تشغيل الحساب الرئيسي: {str(e)}")
        sys.exit()

    await verifyLoggerGroup()
    
    # تحميل الأوامر والملفات
    await load_plugins("plugins")
    await load_plugins("assistant")
    
    # تشغيل الحسابات الفرعية المنصبة داخلياً
    await start_internal_clients()

    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print("᯽︙ سـورس لـوكجـوري يعـمل بـنجاح ✓")
    print(f"تم تشغيل الحسابات والأنلاين تلقائياً")
    print(f"ارسل {cmdhr}الاوامر لـرؤيـة أوامر السورس")
    print("للمسـاعدة: @ee2en | المطور: @rt7r_2")
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    
    await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID != -100:
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    
    await startupmessage()

# تشغيل المحرك الرئيسي
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(luxury_startup())
    except Exception as e:
        LOGS.error(f"❌ خطأ غير متوقع: {e}")
    
    # إبقاء السورس شغالاً
    luxur.run_until_disconnected()