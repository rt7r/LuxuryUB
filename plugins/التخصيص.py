import os
import json
import requests
from urlextract import URLExtract
from JoKeRUB import l313l
from JoKeRUB.core.logger import logging
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from . import BOTLOG_CHATID

LOGS = logging.getLogger(__name__)
extractor = URLExtract()

# =======================================================
# --- دوال قاعدة البيانات (JSON) الشاملة للتنصيب الداخلي ---
# =======================================================
def get_db(client_id):
    db_path = f"vars_{client_id}.json"
    if not os.path.exists(db_path): 
        return {}
    with open(db_path, "r", encoding="utf-8") as f: 
        return json.load(f)

def save_db(client_id, db):
    db_path = f"vars_{client_id}.json"
    with open(db_path, "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=4)
# =======================================================

# --- دالة الرفع الشاملة (بديل تليجراف الفاشل) ---
def upload_to_cloud(file_path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        with open(file_path, 'rb') as f:
            response = requests.post("https://telegra.ph/upload", files={'file': ('file', f, 'image/jpeg')}, headers=headers, timeout=5)
        if response.status_code == 200 and isinstance(response.json(), list):
            return "https://telegra.ph" + response.json()[0]['src']
    except Exception: pass 
    try:
        with open(file_path, 'rb') as f:
            response = requests.post("https://graph.org/upload", files={'file': ('file', f, 'image/jpeg')}, timeout=5)
        if response.status_code == 200 and isinstance(response.json(), list):
            return "https://graph.org" + response.json()[0]['src']
    except Exception: pass 
    try:
        with open(file_path, 'rb') as f:
            response = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=20)
        if response.status_code == 200:
            return response.text.strip() 
    except Exception as e: pass
    return None
# ------------------------------------------------

@l313l.ar_cmd(pattern="جلب (.*)")
async def getvar(event):
    input_str = event.pattern_match.group(1).strip()
    if not input_str:
        return await edit_or_reply(event, "`ضع فار لجلب قيمته`")
    
    client_id = event.sender_id
    db = get_db(client_id)
    val = db.get(input_str)
    
    if val is None:
        return await edit_delete(event, "**⎙ :: عزيزي المستخدم انت لم تقوم باضافه هذا الفار اصلا**")
    await edit_or_reply(event, str(val))

@l313l.ar_cmd(pattern="اضف (.*)")
async def custom_HuRe(event):
    client_id = event.sender_id
    reply = await event.get_reply_message()
    text = reply.text if reply else None
    
    if text is None:
        return await edit_delete(event, "**⌔∮ يجب عليك الرد على النص او الرابط حسب الفار الذي تضيفه **")
    
    input_str = event.pattern_match.group(1).strip()
    var = None
    
    # تحويل الأسماء العربية إلى المتغيرات البرمجية
    if input_str in ["كليشة الحماية", "كليشة الحمايه", "كليشه الحماية", "كليشه الحمايه"]: var = "pmpermit_txt"
    elif input_str in ["اشتراك الخاص", "اشتراك خاص"]: var = "pchan"
    elif input_str in ["اشتراك كروب", "اشتراك الكروب"]: var = "gchan"
    elif input_str in ["امر النشر", "امر نشر"]: var = "MUKRR_ET"
    elif input_str in ["زخرفة الارقام", "زخرفه الارقام"]: var = "JP_FN"
    elif input_str in ["البايو", "بايو"]: var = "DEFAULT_BIO"
    elif input_str in ["رمز الاسم", "علامة الاسم"]: var = "TIME_JEP"
    elif input_str in ["كليشة الفحص", "كليشه الفحص", "كليشه فحص"]: var = "ALIVE_TEMPLATE"
    elif input_str in ["كليشة الحظر", "كليشه الحظر"]: var = "pmblock"
    elif input_str in ["كليشة البوت", "كليشه البوت"]: var = "START_TEXT"
    elif input_str == "ايموجي الفحص": var = "ALIVE_EMOJI"
    elif input_str == "نص الفحص": var = "ALIVE_TEXT"
    elif input_str == "عدد التحذيرات": var = "MAX_FLOOD_IN_PMS"
    elif input_str in ["لون الوقتي", "لون وقتي", "لون صوره وقتيه", "لون الصوره الوقتيه", "لون"]: var = "digitalpiccolor"
    elif input_str in ["التخزين", "تخزين"]: var = "PM_LOGGER_GROUP_ID"
    elif input_str in ["كليشة الخاص", "كليشه الخاص"]: var = "aljoker_message"
    elif input_str in ["اشعارات", "الاشعارات"]: var = "PRIVATE_GROUP_BOT_API_ID"
    else: var = input_str # إذا لم يكن بالقائمة يحفظه باسمه المباشر
        
    if var:
        # الحفظ فقط بنظام JSON
        db = get_db(client_id)
        db[var] = text
        save_db(client_id, db)
        
        await edit_or_reply(event, f"**₰ تم بنجاح تحديث فار {input_str} 𓆰،**")
        if BOTLOG_CHATID:
            await event.client.send_message(BOTLOG_CHATID, f"#اضف_فار\n**{input_str}** تم تحديثه بنجاح كـ:\n{text}")

@l313l.ar_cmd(pattern="حذف (.*)")
async def custom_HuRe_del(event):
    client_id = event.sender_id
    input_str = event.pattern_match.group(1).strip()
    var = None
    
    if input_str in ["كليشة الحماية", "كليشة الحمايه", "كليشه الحماية", "كليشه الحمايه"]: var = "pmpermit_txt"
    elif input_str in ["كليشة الفحص", "كليشه الفحص", "كليشه فحص"]: var = "ALIVE_TEMPLATE"
    elif input_str in ["كليشة الحظر", "كليشه الحظر"]: var = "pmblock"
    elif input_str in ["صورة الحماية", "صورة الحمايه", "صوره الحماية", "صوره الحمايه"]: var = "pmpermit_pic"
    elif input_str in ["لون الوقتي", "لون وقتي", "لون صوره وقتيه", "لون الصوره الوقتيه"]: var = "digitalpiccolor"
    elif input_str in ["صورة الفحص", "صوره الفحص"]: var = "ALIVE_PIC"
    elif input_str in ["كليشة البوت", "كليشه البوت"]: var = "START_TEXT"
    elif input_str == "ايموجي الفحص": var = "ALIVE_EMOJI"
    elif input_str in ["التخزين", "تخزين"]: var = "PM_LOGGER_GROUP_ID"
    elif input_str in ["اشعارات", "الاشعارات"]: var = "PRIVATE_GROUP_BOT_API_ID"
    elif input_str == "نص الفحص": var = "ALIVE_TEXT"
    elif input_str in ["زخرفة الارقام", "زخرفه الارقام"]: var = "JP_FN"
    elif input_str in ["بايو", "البايو"]: var = "DEFAULT_BIO"
    elif input_str == "رمز الاسم": var = "TIME_JEP"
    elif input_str == "عدد التحذيرات": var = "MAX_FLOOD_IN_PMS"
    elif input_str in ["صورة البنك", "صوره البنك"]: var = "PING_PIC"
    else: var = input_str 

    if var:
        db = get_db(client_id)
        if var in db:
            del db[var]
            save_db(client_id, db)
            await edit_or_reply(event, f"₰ هذا الفار ({input_str}) تم حذفه بنجاح وارجاع قيمته الى القيمه الاصلية ✅")
            if BOTLOG_CHATID:
                await event.client.send_message(BOTLOG_CHATID, f"#حذف_فار\n**فار {input_str}** تم حذفه من ملفات النظام")
        else:
            return await edit_delete(event, "**⎙ :: عزيزي المستخدم انت لم تقوم باضافه هذا الفار اصلا**")

# ----------------- أوامر إضافة الصور (مدعومة بـ JSON فقط) -----------------

@l313l.ar_cmd(pattern="اضف صورة (الفحص|فحص) ?(.*)")
async def alive_aljoker(event):
    client_id = event.sender_id
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("**᯽︙ جـارِ رفع الصورة للسيرفرات...**")
        media = await reply.download_media()
        url = upload_to_cloud(media)
        if os.path.exists(media): os.remove(media)
        
        if url:
            db = get_db(client_id)
            db["ALIVE_PIC"] = url
            save_db(client_id, db)
            
            await jokevent.edit(f"**᯽︙ تم بنجاح اضافة صورة {input_str} ✓ **\n**الرابط:** `{url}`")
        else:
            await jokevent.edit("**حدث خطأ أثناء تحميل الصورة! السيرفرات لا تستجيب.**")
    else:
        await event.edit("**᯽︙ يرجى الرد على الصورة لتحديث الفار**")

@l313l.ar_cmd(pattern="اضف صورة (البنك|بنك) ?(.*)")
async def add_ping_aljoker(event):
    client_id = event.sender_id
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("**᯽︙ جـارِ رفع الصورة للسيرفرات...**")
        media = await reply.download_media()
        url = upload_to_cloud(media)
        if os.path.exists(media): os.remove(media)
        
        if url:
            db = get_db(client_id)
            db["PING_PIC"] = url
            save_db(client_id, db)
            
            await jokevent.edit(f"**᯽︙ تم بنجاح اضافة صورة {input_str} ✓ **\n**الرابط:** `{url}`")
        else:
            await jokevent.edit("**حدث خطأ أثناء تحميل الصورة! السيرفرات لا تستجيب.**")
    else:
        await event.edit("**᯽︙ يرجى الرد على الصورة لتحديث الفار**")

@l313l.ar_cmd(pattern="اضف صورة (الحماية|الحمايه|حماية|حمايه) ?(.*)")
async def security_aljoker(event):
    client_id = event.sender_id
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("**᯽︙ جـارِ رفع الصورة للسيرفرات...**")
        media = await reply.download_media()
        url = upload_to_cloud(media)
        if os.path.exists(media): os.remove(media)
        
        if url:
            db = get_db(client_id)
            db["pmpermit_pic"] = url
            save_db(client_id, db)
            
            await jokevent.edit(f"**᯽︙ تم بنجاح اضافة صورة {input_str} ✓ **\n**الرابط:** `{url}`")
        else:
            await jokevent.edit("**حدث خطأ أثناء تحميل الصورة! السيرفرات لا تستجيب.**")
    else:
        await event.edit("** ᯽︙ يرجى الرد على الصورة او فيديو لتحديث الفار **")

@l313l.ar_cmd(pattern="اضف صورة (الخاص|خاص) ?(.*)")
async def al5a9_aljoker(event):
    client_id = event.sender_id
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("**᯽︙ جـارِ رفع الصورة للسيرفرات...**")
        media = await reply.download_media()
        url = upload_to_cloud(media)
        if os.path.exists(media): os.remove(media)
        
        if url:
            db = get_db(client_id)
            db["aljoker_url"] = url
            save_db(client_id, db)
            
            await jokevent.edit(f"**᯽︙ تم بنجاح اضافة صورة {input_str} ✓ **\n**الرابط:** `{url}`")
        else:
            await jokevent.edit("**حدث خطأ أثناء تحميل الصورة! السيرفرات لا تستجيب.**")
    else:
        await event.edit("** ᯽︙ يرجى الرد على الصورة او فيديو لتحديث الفار **")