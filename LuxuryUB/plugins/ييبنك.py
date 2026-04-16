import random
import re
import time
import asyncio
import os
import json
from datetime import datetime
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)

from LuxuryUB import luxur
from telethon import events
from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers.utils import reply_id
from ..sql_helper.globals import gvarstatus

plugin_category = "utils"

#كتـابة وتعـديل:  @lMl10l

# =======================================================
# --- دالة جلب البيانات من JSON (للتنصيب الداخلي) ---
# =======================================================
def get_db(client_id):
    db_path = f"vars_{client_id}.json"
    if not os.path.exists(db_path): 
        return {}
    with open(db_path, "r", encoding="utf-8") as f: 
        return json.load(f)
# =======================================================

@luxur.ar_cmd(pattern="بنك(?:\s|$)([\s\S]*)")
async def jokerping(event):
    client_id = event.sender_id
    db = get_db(client_id)
    
    reply_to_id = await reply_id(event)
    start = datetime.now()
    await edit_or_reply(event, "** ᯽︙ يتـم التـأكـد من البنك انتـظر قليلا رجاءا**")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    
    # الجلب من JSON أولاً، ثم SQL كاحتياط، ثم القيمة الافتراضية
    EMOJI = db.get("ALIVE_EMOJI") or gvarstatus("ALIVE_EMOJI") or "✇ ◅"
    PING_TEXT = db.get("PING_TEXT") or gvarstatus("PING_TEXT") or "**[ 𝗜 𝗝𝘂𝘀𝘁 𝗔𝘀𝗸𝗲𝗱 𝗙𝗼𝗿 𝗦𝗼𝗺𝗲 𝗣𝗲𝗮𝗰𝗲  ](t.me/mn_qv)**"
    PING_IMG = db.get("PING_PIC") or gvarstatus("PING_PIC") or "https://files.catbox.moe/r74kqv.jpg"
    HuRe_caption = db.get("PING_TEMPLATE") or gvarstatus("PING_TEMPLATE") or temp
    
    # === سحب اسمك الحقيقي وعمل منشن قابل للضغط ===
    me = await event.client.get_me()
    first_name = me.first_name or "المطور"
    mention = f"[{first_name}](tg://user?id={me.id})"
    # ========================================================
    
    caption = HuRe_caption.format(
        PING_TEXT=PING_TEXT,
        EMOJI=EMOJI,
        mention=mention,
        ping=ms,
    )
    
    if PING_IMG:
        JEP = [x for x in PING_IMG.split()]
        PIC = random.choice(JEP)
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=caption, reply_to=reply_to_id
            )
            await event.delete()
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                event,
                f"**الميـديا خـطأ **\nغـير الرابـط بأستـخدام الأمـر  \n `.اضف صورة البنك` بالرد على صورتك\n\n**لا يمـكن الحـصول عـلى صـورة من الـرابـط :-** `{PIC}`",
            )
    else:
        await edit_or_reply(
            event,
            caption,
        )


temp = """{PING_TEXT}
┏━━━━━━━┓
┃ ✦ {ping}
┃ ✦ {mention}
┗━━━━━━━┛"""