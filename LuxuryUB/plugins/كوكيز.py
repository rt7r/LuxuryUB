import os
from LuxuryUB import luxur
from telethon import events

@luxur.ar_cmd(
    pattern="تحديث الكوكيز$",
    command=("تحديث الكوكيز", "الميوزك"),
    info={
        "header": "لتحديث ملف الكوكيز الخاص باليوتيوب لتشغيل الاغاني",
        "usage": "{tr}تحديث الكوكيز بالرد على ملف cookies.txt",
    }
)

async def update_cookies(event):
    if not event.reply_to_msg_id:
        return await event.edit("⚠️ لازم ترد على ملف `cookies.txt` الجديد!")
    
    reply = await event.get_reply_message()
    
    # 2. يتأكد إن الملف المرفق هو ملف نصي وصحيح
    if not reply.document or not reply.file.name.endswith(".txt"):
        return await event.edit("⚠️ الملف غلط! تأكد إنك داز ملف اسمه `cookies.txt`.")
    
    await event.edit("⏳ جاري سحب وتحديث الكوكيز بالسيرفر...")
    
    # 3. يحمل الملف ويستبدل القديم بالاستضافة (بنفس المسار الرئيسي)
    file_path = "cookies.txt"
    if os.path.exists(file_path):
        os.remove(file_path) # يمسح القديم
        
    await reply.download_media(file=file_path) # يحفظ الجديد
    
    await event.edit("✅ **تم تحديث الكوكيز بنجاح!**\nعاشت ايدك")