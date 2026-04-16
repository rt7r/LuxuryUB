#من سورس الجوكر+تعديلاتي rt7r_2.t.me
import asyncio
import json
import os
import pytz
import shutil
from datetime import datetime
from telethon import events, functions, types
from PIL import Image, ImageDraw, ImageFont
from pySmartDL import SmartDL
from LuxuryUB.core.session import luxur
from ..Config import Config

# --- نظام العزل والقاعدة ---
def get_db():
    db_path = f"vars_{luxur.uid}.json"
    if not os.path.exists(db_path): return {}
    with open(db_path, "r", encoding="utf-8") as f: return json.load(f)

def save_db(db):
    db_path = f"vars_{luxur.uid}.json"
    if not os.path.exists(db_path): return {}
    with open(db_path, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

def get_font(num_str, db):
    font = db.get("JP_FN", "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎")
    norm = "1234567890"
    return "".join(font[norm.index(n)] if n in norm else n for n in num_str)

# --- محرك الوقتي ---
async def time_loop():
    while not luxur.is_connected(): await asyncio.sleep(1)
    while True:
        db = get_db()
        if not db: 
            await asyncio.sleep(60)
            continue
            
        tz_name = db.get("TZ", "Asia/Baghdad")
        now = datetime.now(pytz.timezone(tz_name))
        hm = now.strftime("%I:%M")
        z_hm = get_font(hm, db)
        
        # 1. الاسم الوقتي
        if db.get("autoname") == "true":
            try:
                me = await luxur.get_me()
                first_n = db.get("ALIVE_NAME") or me.first_name
                last_n = f"{z_hm} {db.get('TIME_JEP', '')}".strip()
                await luxur(functions.account.UpdateProfileRequest(first_name=first_n, last_name=last_n))
            except: pass

        # 2. البايو الوقتي
        if db.get("autobio") == "true":
            try:
                bio = f"{db.get('DEFAULT_BIO', 'إِنَّ ٱللَّهَ وَمَلَٰٓئِكَتَهُۥ يُصَلُّونَ عَلَى ٱلنَّبِيِّۚ يَٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُواْ صَلُّواْ عَلَيۡهِ وَسَلِّمُواْ تَسۡلِيمًا ٥٦')} | {z_hm}"
                await luxur(functions.account.UpdateProfileRequest(about=bio[:70]))
            except: pass

        # 3. الصورة الوقتية
        if db.get("digitalpic") == "true":
            try:
                img_url = db.get("DIGITAL_PIC", "https://telegra.ph/file/63a826d5e5f0003e006a0.jpg")
                p_path = f"pfp_{luxur.uid}.png"
                if not os.path.exists(p_path):
                    SmartDL(img_url, p_path, progress_bar=False).start(blocking=True)
                img = Image.open(p_path)
                draw = ImageDraw.Draw(img)
                fnt = ImageFont.truetype("LuxuryUB/helpers/styles/PaybAck.ttf", 65)
                draw.text((200, 200), hm, font=fnt, fill="white")
                img.save("upload.png")
                await luxur(functions.photos.UploadProfilePhotoRequest(file=await luxur.upload_file("upload.png")))
            except: pass

        # 4. الكروب الوقتي
        if db.get("digitalgroup"):
            try:
                chid = int(db.get("digitalgroup"))
                await luxur(functions.channels.EditTitleRequest(channel=chid, title=f"{db.get('DEFAULT_GROUP', 'Group')} {z_hm}"))
            except: pass

        await asyncio.sleep(60)

# --- أوامر التفعيل ---
@luxur.ar_cmd(pattern="(اسم وقتي|بايو وقتي|الصورة الوقتية)$")
async def start_time(event):
    mode = event.pattern_match.group(1)
    db = get_db()
    me = await event.client.get_me()
    if "اسم" in mode:
        db["autoname"] = "true"
        db["ALIVE_NAME"] = me.first_name
        db["ALIVE_LAST"] = me.last_name or ""
    elif "بايو" in mode:
        db["autobio"] = "true"
        full = await event.client(functions.users.GetFullUserRequest(id=me.id))
        db["DEFAULT_BIO"] = full.full_user.about or ""
    else:
        db["digitalpic"] = "true"
    save_db(db)
    await event.edit(f"**᯽︙ تم تفعيل {mode} بنجاح ✓**")

# --- أوامر الإنهاء مع الاسترجاع الكامل ---
@luxur.ar_cmd(pattern="انهاء (اسم وقتي|بايو وقتي|الصورة الوقتية)$")
async def stop_time(event):
    mode = event.pattern_match.group(1)
    db = get_db()
    me = await event.client.get_me()
    if "اسم" in mode:
        db["autoname"] = "false"
        await event.client(functions.account.UpdateProfileRequest(
            first_name=db.get("ALIVE_NAME", me.first_name), 
            last_name=db.get("ALIVE_LAST", "")
        ))
    elif "بايو" in mode:
        db["autobio"] = "false"
        await event.client(functions.account.UpdateProfileRequest(about=db.get("DEFAULT_BIO", "")))
    elif "الصورة" in mode:
        db["digitalpic"] = "false"
        photos = await event.client(functions.photos.GetUserPhotosRequest(user_id=me.id, offset=0, limit=1, max_id=0))
        if photos.photos:
            await event.client(functions.photos.DeletePhotosRequest(id=[photos.photos[0]]))
    save_db(db)
    await event.edit(f"**᯽︙ تم إنهاء {mode} واسترجاع الحساب للافتراضي ✓**")

@luxur.ar_cmd(pattern="كروب (وقتي|صورة وقتي)$")
async def group_time(event):
    db = get_db()
    chat = await event.get_chat()
    db["digitalgroup"] = str(event.chat_id)
    db["DEFAULT_GROUP"] = chat.title
    save_db(db)
    await event.edit(f"**᯽︙ تم تفعيل الوقتي لهذا الكروب ✓**")

@luxur.ar_cmd(pattern="انهاء كروب وقتي$")
async def stop_group_time(event):
    db = get_db()
    chid = int(db.get("digitalgroup", event.chat_id))
    try:
        await event.client(functions.channels.EditTitleRequest(channel=chid, title=db.get("DEFAULT_GROUP", "Group")))
    except: pass
    db.pop("digitalgroup", None)
    save_db(db)
    await event.edit(f"**᯽︙ تم إنهاء وقتي الكروب واسترجاع الاسم ✓**")

# تشغيل الماطور بدون فراغات زايدة
luxur.loop.create_task(time_loop())