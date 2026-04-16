import asyncio, glob, io, os, re, ujson
from pathlib import Path
from time import time
from telethon import Button, types
from telethon.errors import BotResponseTimeoutError
from telethon.events import CallbackQuery
from telethon.utils import get_attributes
from wget import download
from LuxuryUB import luxur
from ..Config import Config
from ..core import check_owner, pool
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import post_to_telegraph, progress, reply_id
from ..helpers.functions.utube import (
    _mp3Dl, _tubeDl, download_button, get_choice_by_id, get_ytthumb, yt_search_btns
)
from ..plugins import BOTLOG_CHATID

LOGS = logging.getLogger("Luxury-YT")
BASE_YT_URL = "https://www.youtube.com/watch?v="
PATH = "./LuxuryUB/cache/ytsearch.json"

# ==================== أمر البحث (اغنيه) ====================
@luxur.ar_cmd(pattern="اغنيه(?:\s|$)([\s\S]*)")
async def iytdl_inline(event):
    reply = await event.get_reply_message()
    reply_to_id = await reply_id(event)
    input_str = event.pattern_match.group(1) or (reply.text if reply else None)
    
    if not input_str:
        return await edit_delete(event, "**💎 عذراً، اكتب اسم الأغنية أو الرابط أولاً !**")
    
    catevent = await edit_or_reply(event, f"**💎 جاري البحث في يوتيوب لـ :**\n`'{input_str}'`")
    
    try:
        # البحث عبر البوت المساعد (Inline)
        results = await event.client.inline_query(Config.TG_BOT_USERNAME, f"ytdl {input_str}")
        if results:
            await catevent.delete()
            await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
        else:
            await catevent.edit("**💎 لم أجد نتائج، تأكد من الاسم وحاول مجدداً ✘**")
    except Exception as e:
        await catevent.edit(f"**⚠️ حدث خطأ أثناء البحث:** `{str(e)}`")

# ==================== معالجة التحميل (Download) ====================
@luxur.tgbot.on(CallbackQuery(data=re.compile(b"^ytdl_download_(.*)_([\d]+|mkv|mp4|mp3)(?:_(a|v))?")))
@check_owner
async def ytdl_download_callback(c_q: CallbackQuery):
    yt_code = c_q.pattern_match.group(1).decode("UTF-8")
    choice_id = c_q.pattern_match.group(2).decode("UTF-8")
    downtype = c_q.pattern_match.group(3).decode("UTF-8") if c_q.pattern_match.group(3) else None
    
    if str(choice_id).isdigit() and int(choice_id) == 0:
        await c_q.answer("💎 جاري تجهيز خيارات الجودة ...", alert=False)
        return await c_q.edit(buttons=(await download_button(yt_code)))

    startTime = time()
    choice_str, disp_str = get_choice_by_id(int(choice_id) if str(choice_id).isdigit() else choice_id, downtype)
    
    await c_q.answer(f"💎 بدأ التحميل: {disp_str}\nيرجى الانتظار ...", alert=True)
    yt_url = BASE_YT_URL + yt_code
    
    # عملية التحميل الفعلي
    if downtype == "v":
        retcode = await _tubeDl(url=yt_url, starttime=startTime, uid=choice_str)
    else:
        retcode = await _mp3Dl(url=yt_url, starttime=startTime, uid=choice_str)

    if retcode != 0: return await c_q.edit(f"**❌ فشل التحميل:** `{retcode}`")

    # جلب الملف والبوستر من الكاش
    _fpath, thumb_pic = "", None
    for p in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
        if p.lower().endswith((".jpg", ".png", ".webp")): thumb_pic = p
        else: _fpath = p

    if not _fpath: return await c_q.edit("**❌ خطأ: لم أجد الملف المحمل !**")

    # الرفع للقناة (Log) وللمستخدم
    await c_q.edit(f"**💎 جاري رفع الملف :**\n`{os.path.basename(_fpath)}`")
    await c_q.client.send_file(c_q.chat_id, file=_fpath, caption=f"**💎 تم التحميل بواسطة لوكجوري\nالملف:** `{os.path.basename(_fpath)}`", thumb=thumb_pic)

# ==================== التنقل بين النتائج (Navigation) ====================
@luxur.tgbot.on(CallbackQuery(data=re.compile(b"^ytdl_(listall|back|next|detail)_([a-z0-9]+)_(.*)")))
@check_owner
async def ytdl_callback(c_q: CallbackQuery):
    btn, key, page = [x.decode("utf-8") if isinstance(x, bytes) else x for x in c_q.pattern_match.groups()]
    
    if not os.path.exists(PATH):
        return await c_q.answer("💎 انتهت صلاحية البحث، ابحث مجدداً.", alert=True)

    with open(PATH) as f: search_data = ujson.load(f).get(key)
    total = len(search_data) if search_data else 0

    if btn == "next" or btn == "back":
        index = int(page) + (1 if btn == "next" else -1)
        if 1 <= index <= total:
            vid = search_data.get(str(index))
            await c_q.edit(text=vid.get("message"), file=await get_ytthumb(vid.get("video_id")), 
                           buttons=yt_search_btns(del_back=(index==1), data_key=key, page=index, vid=vid.get("video_id"), total=total), parse_mode="html")
    
    elif btn == "listall":
        telegraph = await post_to_telegraph("نتائج يوتيوب 💎", "".join(search_data.get(v).get("list_view") for v in search_data))
        await c_q.edit(buttons=[[Button.url("↗️ القائمة كاملة", telegraph)], [Button.inline("📰 العرض التفصيلي", f"ytdl_detail_{key}_{page}", style="success")]])