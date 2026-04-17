import os
import random
import asyncio
import re
from yt_dlp import YoutubeDL
from telethon import events, functions

# 🚀 استدعاءات أحدث نسخة من الكيت هاب (API v5)
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

from LuxuryUB import luxur
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..sql_helper.globals import gvarstatus, addgvar

# ==================== الإعدادات المتطورة ====================
YDL_AUDIO_OPTS = {
    "format": "bestaudio/best", 
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
}

YDL_VIDEO_OPTS = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
}

# ==================== الذاكرة المؤقتة ====================
call_app = None 
playlist = {} # {chat_id: [{"title": title, "url": url_or_path, "is_video": bool}]}
authorized_users = {} # {owner_id: set(user_ids)}

# ==================== دوال التهيئة ====================
# ==================== دوال التهيئة ====================
async def get_app(client):
    global call_app
    if call_app is None:
        # 🚀 الضربة القاضية: نزور هوية الكلاينت حتى تقبله المكتبة غصباً عليها
        client.__class__.__module__ = "telethon.client.telegramclient"
        
        call_app = PyTgCalls(client)
        await call_app.start()
        
        # 🤖 نظام التخطي التلقائي (من يخلص مقطع يشغل البعده)
        @call_app.on_stream_end()
        async def on_stream_end_handler(client, update):
            chat_id = update.chat_id
            if chat_id in playlist and len(playlist[chat_id]) > 0:
                next_item = playlist[chat_id].pop(0)
                media = MediaStream(next_item["url"])
                await call_app.play(chat_id, media)
            else:
                try:
                    await call_app.leave_call(chat_id)
                except:
                    pass
                
    return call_app
        


def is_music_enabled(owner_id):
    return gvarstatus(owner_id, "MUSIC_STATUS") == "true"

# ==================== 1. تفعيل وتعطيل ====================
@luxur.ar_cmd(pattern="(تفعيل|تعطيل) الميوزك$")
async def toggle_music(event):
    owner_id = (await event.client.get_me()).id
    status = "true" if "تفعيل" in event.text else "false"
    addgvar(owner_id, "MUSIC_STATUS", status)
    await edit_or_reply(event, f"**💎 تم {'تفعيل' if status=='true' else 'تعطيل'} نظام الميوزك بنجاح ✓**")

# ==================== 7. إدارة المشغلين ====================
@luxur.ar_cmd(pattern="(مشغل|حذف المشغلين)$")
async def manage_operators(event):
    owner_id = (await event.client.get_me()).id
    if owner_id not in authorized_users: authorized_users[owner_id] = set()
    
    if "حذف" in event.text:
        authorized_users[owner_id].clear()
        return await edit_or_reply(event, "**🗑️ تم حذف جميع المشغلين بنجاح.**")
    
    reply = await event.get_reply_message()
    if reply:
        authorized_users[owner_id].add(reply.sender_id)
        await edit_or_reply(event, f"**✅ تم إضافة `{reply.sender_id}` لقائمة المشغلين.**")
    else:
        await edit_or_reply(event, "**⚠️ يرجى الرد على المستخدم لإضافته كمشغل.**")

# ==================== المحرك المركزي لمعالجة الأوامر ====================
# الكلمات المفتاحية كلها هنا
MUSIC_CMDS = "(شغل 1|شغل فيديو|شغل|تشغيل|فيديو 1|فيديو|انضمام|مغادرة|فتح مكالمة|اطفاء مكالمة|تخطي|وكف مؤقتا|وكف|وقف|كمل|استمرار|ايقاف نهائي|ايقاف|قائمة التشغيل)"

async def process_music_command(event, cmd, target_id_str, query, reply):
    owner_id = (await event.client.get_me()).id
    if not is_music_enabled(owner_id):
        return await event.reply("**⚠️ نظام الميوزك معطل حالياً.**")

    # استخراج وتحديد الـ ID
    chat_id = int(target_id_str) if target_id_str else event.chat_id
    app = await get_app(event.client)
    
    # ---------------- 6. فتح واغلاق المكالمة ----------------
    if cmd in ["فتح مكالمة"]:
        try:
            await event.client(functions.phone.CreateGroupCallRequest(peer=chat_id, random_id=random.randint(10000, 999999999)))
            return await event.reply(f"**✅ تم فتح المكالمة الصوتية في :** `{chat_id}`")
        except:
            return await event.reply("**⚠️ المكالمة مفتوحة بالفعل.**")
            
    if cmd in ["اطفاء مكالمة"]:
        try:
            full_chat = await event.client(functions.channels.GetFullChannelRequest(chat_id))
            if full_chat.full_chat.call:
                await event.client(functions.phone.DiscardGroupCallRequest(call=full_chat.full_chat.call))
                return await event.reply(f"**❌ تم إنهاء المكالمة الصوتية في :** `{chat_id}`")
            return await event.reply("**⚠️ لا توجد مكالمة نشطة لإنهائها.**")
        except Exception as e:
            return await event.reply(f"**❌ خطأ:** `{str(e)}`")

    # ---------------- 4. انضمام / 5. مغادرة ----------------
    if cmd in ["انضمام"]:
        try:
            await event.client(functions.phone.CreateGroupCallRequest(peer=chat_id, random_id=random.randint(10000, 999999999)))
        except:
            pass # إذا مفتوحة غلس
        return await event.reply("**✅ تم تجهيز المكالمة الصوتية للانضمام، يرجى تشغيل مقطع.**")

    if cmd in ["مغادرة"]:
        try:
            await app.leave_call(chat_id)
            return await event.reply("**⏹️ تم مغادرة المكالمة.**")
        except:
            return await event.reply("**⚠️ الحساب ليس في المكالمة أصلاً.**")

    # ---------------- أوامر التحكم ----------------
    if cmd in ["وكف مؤقتا", "وكف", "وقف"]:
        await app.pause(chat_id)
        return await event.reply("**⏸️ تم إيقاف التشغيل مؤقتاً.**")
        
    if cmd in ["كمل", "استمرار"]:
        await app.resume(chat_id)
        return await event.reply("**▶️ تم استئناف التشغيل.**")
        
    if cmd in ["ايقاف نهائي", "ايقاف"]:
        try:
            await app.leave_call(chat_id)
        except: pass
        if chat_id in playlist: playlist[chat_id].clear() # تصفير القائمة
        return await event.reply("**⏹️ تم إيقاف التشغيل نهائياً وتصفير قائمة التشغيل.**")
        
    if cmd in ["تخطي"]:
        if chat_id in playlist and len(playlist[chat_id]) > 0:
            next_item = playlist[chat_id].pop(0)
            await app.play(chat_id, MediaStream(next_item["url"]))
            return await event.reply(f"**⏭️ تم التخطي، يتم الآن تشغيل:** `{next_item['title']}`")
        else:
            try: await app.leave_call(chat_id) 
            except: pass
            return await event.reply("**⏹️ القائمة فارغة، تم إيقاف التشغيل.**")
            
    if cmd in ["قائمة التشغيل"]:
        if chat_id not in playlist or len(playlist[chat_id]) == 0:
            return await event.reply("**📭 قائمة التشغيل فارغة.**")
        text = "**📑 قائمة التشغيل الحالية:**\n\n"
        for i, item in enumerate(playlist[chat_id], 1):
            text += f"**{i}.** `{item['title']}`\n"
        return await event.reply(text)

    # ---------------- 2. و 3. التشغيل بكل أنواعه ----------------
    if cmd in ["شغل", "تشغيل", "شغل 1", "فيديو", "شغل فيديو", "فيديو 1"]:
        proc = await event.reply("**💎 جاري معالجة الطلب وبدء البث ...**")
        
        is_video = "فيديو" in cmd or (reply and reply.video)
        is_force = "1" in cmd # هل هو تشغيل إجباري (شغل 1 أو فيديو 1)؟
        
        url_or_path = ""
        title = ""

        try:
            # حالة الرد على ملف
            if reply and (reply.audio or reply.video or reply.voice):
                await proc.edit("**📥 جاري تحميل الملف للاستضافة...**") 
                url_or_path = await reply.download_media()
                title = "ملف مرفق 📁"
                
            # حالة البحث بالاسم أو الرابط
            elif query or (reply and reply.text):
                search_query = query or reply.text
                await proc.edit(f"**💎 جاري البحث واستخراج البيانات...**\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")

                opts = YDL_VIDEO_OPTS if is_video else YDL_AUDIO_OPTS
                with YoutubeDL(opts) as ydl:
                    if not search_query.startswith("http"):
                        info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                        if info and 'entries' in info and info['entries']:
                            info = info['entries'][0] 
                        else:
                            return await proc.edit("**❌ لم يتم العثور على نتائج.**")
                    else:
                        info = ydl.extract_info(search_query, download=False)
                    
                    url_or_path = info.get("url")
                    title = info.get("title", "مقطع غير معروف")
            else:
                return await proc.edit("**⚠️ يرجى كتابة اسم الأغنية أو الرد على ملف.**")

            if not url_or_path:
                return await proc.edit("**❌ فشل في استخراج رابط البث.**")

            media = MediaStream(url_or_path)
            
            # إذا تشغيل إجباري (شغل 1)، صفر القائمة
            if is_force:
                if chat_id in playlist: playlist[chat_id].clear()
            
            # فحص إذا اكو شي يشتغل حالياً
            active_call = app.active_calls.get(chat_id)
            
            if active_call and not is_force:
                # إضافة للطابور
                if chat_id not in playlist: playlist[chat_id] = []
                playlist[chat_id].append({"title": title, "url": url_or_path, "is_video": is_video})
                return await proc.edit(f"**⏳ تمت الإضافة إلى قائمة التشغيل:**\n`{title}`\n**الترتيب:** `{len(playlist[chat_id])}`")
            else:
                # تشغيل مباشر (أو إجباري)
                try:
                    await app.play(chat_id, media)
                except Exception as e:
                    if "NoActiveGroupCall" in str(e) or "not found" in str(e).lower():
                        await event.client(functions.phone.CreateGroupCallRequest(peer=chat_id, random_id=random.randint(10000, 999999999)))
                        await asyncio.sleep(2)
                        await app.play(chat_id, media)
                    else:
                        raise e
                return await proc.edit(f"**🎶 يتم الآن تشغيل:**\n`{title}`\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")

        except Exception as e:
            return await proc.edit(f"**⚠️ خطأ:** `{str(e)}`")

# ==================== استقبال أوامر المالك ====================
@luxur.ar_cmd(pattern=f"{MUSIC_CMDS}(?: -id (-\d+|\d+))?(?:\s|$)([\s\S]*)")
async def owner_music_handler(event):
    cmd = event.pattern_match.group(1)
    target_id_str = event.pattern_match.group(2)
    query = event.pattern_match.group(3).strip() if event.pattern_match.group(3) else None
    reply = await event.get_reply_message()
    await process_music_command(event, cmd, target_id_str, query, reply)

# ==================== استقبال أوامر المشغلين ====================
@luxur.on(events.NewMessage(incoming=True))
async def operator_listener(event):
    owner_id = (await event.client.get_me()).id
    sender_id = event.sender_id
    
    # 1. هل الشخص مشغل معتمد؟
    if sender_id not in authorized_users.get(owner_id, set()):
        return
        
    text = event.raw_text.strip()
    
    # 2. مطابقة الأوامر
    match = re.match(f"^{MUSIC_CMDS}(?: -id (-\d+|\d+))?(?:\s|$)([\s\S]*)", text)
    if match:
        cmd = match.group(1)
        target_id_str = match.group(2)
        query = match.group(3).strip() if match.group(3) else None
        reply = await event.get_reply_message()
        
        # 3. حظر المشغل من الأوامر الممنوعة (المغادرة والاطفاء والايقاف النهائي)
        forbidden_cmds = ["مغادرة", "ايقاف نهائي", "اطفاء مكالمة"]
        if cmd in forbidden_cmds:
            return await event.reply("**⚠️ عذراً، لا تمتلك صلاحية لهذا الأمر.**")
            
        await process_music_command(event, cmd, target_id_str, query, reply)