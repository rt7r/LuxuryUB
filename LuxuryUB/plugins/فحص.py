import random
import re
import time
import asyncio
import os
import json
import pytz
from datetime import datetime
from platform import python_version
from telethon import version
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.events import CallbackQuery

from LuxuryUB import StartTime, luxur, JEPVERSION
from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers.functions import catalive, check_data_base_heal_th, get_readable_time
from ..helpers.utils import reply_id
from ..sql_helper.globals import gvarstatus

plugin_category = "utils"

# تعديل وتطوير: @rt7r_2 | سورس لوكجوري
file_path = "installation_date.txt"
if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    with open(file_path, "r") as file:
        installation_time = file.read().strip()
else:
    installation_time = datetime.now().strftime("%Y-%m-%d")
    with open(file_path, "w") as file:
        file.write(installation_time)

# ================= نظام جلب البيانات (JSON + SQL) =================
def get_db(client_id):
    db_path = f"vars_{client_id}.json"
    if not os.path.exists(db_path): 
        return {}
    with open(db_path, "r", encoding="utf-8") as f: 
        return json.load(f)

@luxur.ar_cmd(pattern="فحص(?:\s|$)([\s\S]*)")
async def amireallyalive(event):
    # استخدام ايدي المرسل لضمان تعدد المستخدمين
    client_id = event.sender_id
    db = get_db(client_id)
    
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    await edit_or_reply(event, "** ᯽︙ يتـم التـأكـد انتـظر قليلا رجاءا**")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    _, check_sgnirts = check_data_base_heal_th()
    
    # جلب الإعدادات مع تمرير client_id لنظام الـ SQL المطور
    EMOJI = db.get("ALIVE_EMOJI") or gvarstatus(client_id, "ALIVE_EMOJI") or "⿻┊‌‎"
    ALIVE_TEXT = db.get("ALIVE_TEXT") or gvarstatus(client_id, "ALIVE_TEXT") or "**父[ LUXURY IS WORKING ✓ ](t.me/ee2en)父**"
    HuRe_IMG = db.get("ALIVE_PIC") or gvarstatus(client_id, "ALIVE_PIC") or Config.A_PIC
    luxur_caption = db.get("ALIVE_TEMPLATE") or gvarstatus(client_id, "ALIVE_TEMPLATE") or temp
    
    me = await luxur.get_me()
    first_name = me.first_name or "المطور"
    mention = f"[{first_name}](tg://user?id={me.id})"
    
    baghdad_tz = pytz.timezone("Asia/Baghdad")
    now_time = datetime.now(baghdad_tz)
    current_time = now_time.strftime("%I:%M %p")
    current_date = now_time.strftime("%Y/%m/%d")

    caption = luxur_caption.format(
        ALIVE_TEXT=ALIVE_TEXT,
        EMOJI=EMOJI,
        mention=mention,
        uptime=uptime,
        telever=version.__version__,
        jepver=JEPVERSION,
        pyver=python_version(),
        dbhealth=check_sgnirts,
        ping=ms,
        Tare5=installation_time,
        time=current_time,
        date=current_date, 
    )
    
    # تم حذف كود الـ base64 والانضمام الإجباري لضمان خصوصيتك وسرعة البوت
        
    if HuRe_IMG:
        LuxuryUB_list = [x for x in HuRe_IMG.split()]
        PIC = random.choice(LuxuryUB_list)
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=caption, reply_to=reply_to_id
            )
            await event.delete()
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                event,
                f"**الميـديا خـطأ **\nغـير الرابـط بأستـخدام الأمـر \n `.اضف صورة الفحص` بالرد على صورتك\n\n**لا يمـكن الحـصول عـلى صـورة من الـرابـط :-** `{PIC}`",
            )
    else:
        await edit_or_reply(event, caption)

# الكليشة الأصلية كما طلبتها بالضبط
temp = """⟣⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⟢
   ⎙ :‌‎𝑶𝒘𝒏𝒆𝒓 ⌯ {mention} ٫
   ⎙ :‌‎𝒑𝒚𝒕𝒉𝒐𝒏 ⌯  {pyver} ٫
   
   ⎙ :‌‎𝒕𝒆𝒍𝒆𝒕𝒉𝒐𝒏 {telever} ٫
   ⎙ :‌‎𝒖𝒑 𝒕𝒊𝒎𝒆 ⌯ {uptime} ٫
   
   ‌‎⎙ :‌‎‌‎𝑷𝒊𝒏𝒈 ⌯  {ping} ٫
   ‌‎⎙ :‌‎‌‎𝑺𝒆𝒕𝒖𝒑 𝑫𝒂𝒕𝒆 ⌯ {date} ٫
   ‌‎⎙ :‌‎‌‎𝑻𝒊𝒎𝒆 ⌯ {time} ٫
⟣⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⟢"""