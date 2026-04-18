import os
import random
import asyncio
import re
from yt_dlp import YoutubeDL
from telethon import events, functions

# 🚀 استدعاءات النسخة القديمة المستقرة (dev24)
from pytgcalls.group_call_factory import GroupCallFactory, MTProtoClientType

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
    "extractor_args": {"youtube": {"player_client": ["web", "mweb"]}}
}

# 🛡️ إجبار يوتيوب على سحب دقة 720p أو 480p كحد أقصى حتى لا يفصل البث
YDL_VIDEO_OPTS = {
    "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best", 
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "extractor_args": {"youtube": {"player_client": ["web", "mweb"]}}
}

# ==================== الذاكرة المؤقتة (Smart Tracking) ====================
active_calls = {} # {owner_id: call_instance}
is_playing = {} # دفتر ملاحظات البوت: {chat_id: True/False}
playlist = {} # قائمة التشغيل: {chat_id: [{"title": title, "url": url_or_path, "is_video": bool}]}
authorized_users = {} # المشغلين: {owner_id: set(user_ids)}

# ==================== دالة التحقق ====================
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
MUSIC_CMDS = "(شغل 1|شغل فيديو|شغل|تشغيل|فيديو 1|فيديو|انضمام|مغادرة|فتح مكالمة|اطفاء مكالمة|حالة المكالمة|تخطي|وكف مؤقتا|وكف|وقف|كمل|استمرار|ايقاف نهائي|ايقاف|قائمة التشغيل)"

async def process_music_command(event, cmd, target_id_str, query, reply):
    owner_id = (await event.client.get_me()).id
    if not is_music_enabled(owner_id):
        return await event.reply("**⚠️ نظام الميوزك معطل حالياً.**")

    # تحديد الـ ID
    chat_id = int(target_id_str) if target_id_str else event.chat_id
    
    # تهيئة محرك الاتصال الخاص بـ dev24
    if owner_id not in active_calls:
        active_calls[owner_id] = GroupCallFactory(event.client, MTProtoClientType.TELETHON).get_group_call()
    call = active_calls[owner_id]
    
    # ---------------- 6. إدارة المكالمة ----------------
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
                is_playing[chat_id] = False
                if chat_id in playlist: playlist[chat_id].clear()
                return await event.reply(f"**❌ تم إنهاء المكالمة الصوتية في :** `{chat_id}`")
            return await event.reply("**⚠️ لا توجد مكالمة نشطة لإنهائها.**")
        except Exception as e:
            return await event.reply(f"**❌ خطأ:** `{str(e)}`")

    if cmd in ["حالة المكالمة"]:
        try:
            call_info = await event.client(functions.phone.GetGroupCallRequest(peer=chat_id))
            return await event.reply(f"**📊 حالة المكالمة :**\n**العنوان:** `{call_info.call.title or 'لا يوجد'}`\n**المشاركين:** `{call_info.call.participants_count}`")
        except:
            return await event.reply("**⚠️ لا توجد مكالمة نشطة هنا.**")

    # ---------------- 4. انضمام / 5. مغادرة ----------------
    if cmd in ["انضمام"]:
        try:
            await call.join(chat_id)
            return await event.reply("**✅ تم تجهيز المكالمة الصوتية والانضمام بنجاح.**")
        except Exception as e:
            return await event.reply(f"**⚠️ خطأ في الانضمام:** `{str(e)}`")

    if cmd in ["مغادرة"]:
        try:
            await call.stop()
            is_playing[chat_id] = False
            return await event.reply("**⏹️ تم مغادرة المكالمة.**")
        except:
            return await event.reply("**⚠️ الحساب ليس في المكالمة أصلاً.**")

    # ---------------- أوامر التحكم ----------------
    if cmd in ["وكف مؤقتا", "وكف", "وقف"]:
        try:
            await call.pause_playout()
            return await event.reply("**⏸️ تم إيقاف التشغيل مؤقتاً.**")
        except Exception as e: return await event.reply(f"**⚠️ خطأ:** `{str(e)}`")
        
    if cmd in ["كمل", "استمرار"]:
        try:
            await call.resume_playout()
            return await event.reply("**▶️ تم استئناف التشغيل.**")
        except Exception as e: return await event.reply(f"**⚠️ خطأ:** `{str(e)}`")
        
    if cmd in ["ايقاف نهائي", "ايقاف"]:
        try:
            await call.stop_audio()
            await call.stop_video()
        except: pass
        is_playing[chat_id] = False
        if chat_id in playlist: playlist[chat_id].clear() 
        return await event.reply("**⏹️ تم إيقاف التشغيل نهائياً وتصفير قائمة التشغيل.**")
        
    if cmd in ["تخطي"]:
        if chat_id in playlist and len(playlist[chat_id]) > 0:
            next_item = playlist[chat_id].pop(0)
            try:
                await call.join(chat_id)
                if next_item["is_video"]:
                    await call.start_video(next_item["url"], repeat=False)
                else:
                    await call.start_audio(next_item["url"], repeat=False)
                is_playing[chat_id] = True
                return await event.reply(f"**⏭️ تم التخطي، يتم الآن تشغيل:** `{next_item['title']}`")
            except Exception as e:
                return await event.reply(f"**⚠️ خطأ أثناء التخطي:** `{str(e)}`")
        else:
            try:
                await call.stop_audio()
                await call.stop_video()
            except: pass
            is_playing[chat_id] = False
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
        is_force = "1" in cmd 
        
        url_or_path = ""
        title = ""

        try:
            # 🚀 معالجة الرد على ملفات (مع الضغط التلقائي للفيديو)
            if reply and (reply.audio or reply.video or reply.voice):
                await proc.edit("**📥 جاري تحميل الملف للاستضافة...**") 
                url_or_path = await reply.download_media()
                title = "ملف مرفق 📁"
                
                # سر الخلطة: تخفيض دقة الفيديو لـ 480p حتى يقبله تليجرام
                if is_video:
                    await proc.edit("**⚙️ جاري تعديل دقة الفيديو ليتوافق مع المكالمة (ثواني بس)...**")
                    out_path = f"luxury_vid_{random.randint(1000, 99999)}.mp4"
                    # أمر الضغط السريع جداً (ultrafast)
                    ff_cmd = f'ffmpeg -y -i "{url_or_path}" -vf "scale=-2:480" -c:v libx264 -preset ultrafast -crf 28 -c:a copy "{out_path}"'
                    process = await asyncio.create_subprocess_shell(ff_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                    await process.communicate()
                    
                    if os.path.exists(out_path):
                        try: os.remove(url_or_path) # مسح الخام الثقيل
                        except: pass
                        url_or_path = out_path # الاعتماد على الخفيف المدمج
                
            # حالة البحث بالاسم أو الرابط
            elif query or (reply and reply.text):
                search_query = query or reply.text
                await proc.edit(f"**💎 جاري البحث واستخراج البيانات...**\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")

                opts = YDL_VIDEO_OPTS if is_video else YDL_AUDIO_OPTS
                with YoutubeDL(opts) as ydl:
                    if not search_query.startswith("http"):
                        search_query = f"ytsearch:{search_query}"
                        
                    info = ydl.extract_info(search_query, download=False)
                    
                    if info and 'entries' in info and info['entries']:
                        info = info['entries'][0] 
                        
                    if not info:
                        return await proc.edit("**❌ لم يتم العثور على نتائج.**")
                        
                    url_or_path = info.get("url")
                    title = info.get("title", "مقطع غير معروف")
            else:
                return await proc.edit("**⚠️ يرجى كتابة اسم الأغنية أو الرد على ملف.**")

            if not url_or_path:
                return await proc.edit("**❌ فشل في استخراج رابط البث.**")
            
            # إذا تشغيل إجباري يمسح الملاحظات والطابور
            if is_force:
                if chat_id in playlist: playlist[chat_id].clear()
                is_playing[chat_id] = False 
            
            # 🧠 الذكاء: فحص الطابور
            if is_playing.get(chat_id) and not is_force:
                if chat_id not in playlist: playlist[chat_id] = []
                playlist[chat_id].append({"title": title, "url": url_or_path, "is_video": is_video})
                return await proc.edit(f"**⏳ تمت الإضافة إلى قائمة التشغيل:**\n`{title}`\n**الترتيب في الطابور:** `{len(playlist[chat_id])}`")
            else:
                try:
                    await call.join(chat_id)
                    if is_video:
                        await call.start_video(url_or_path, repeat=False)
                    else:
                        await call.start_audio(url_or_path, repeat=False)
                    is_playing[chat_id] = True # تسجيل الكروب بالدفتر
                except Exception as e:
                    return await proc.edit(f"**⚠️ فشل البث المباشر:** `{str(e)}`")
                    
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
    
    if sender_id not in authorized_users.get(owner_id, set()):
        return
        
    text = event.raw_text.strip()
    
    match = re.match(f"^{MUSIC_CMDS}(?: -id (-\d+|\d+))?(?:\s|$)([\s\S]*)", text)
    if match:
        cmd = match.group(1)
        target_id_str = match.group(2)
        query = match.group(3).strip() if match.group(3) else None
        reply = await event.get_reply_message()
        
        forbidden_cmds = ["مغادرة", "ايقاف نهائي", "اطفاء مكالمة"]
        if cmd in forbidden_cmds:
            return await event.reply("**⚠️ عذراً، لا تمتلك صلاحية لهذا الأمر.**")
            
        await process_music_command(event, cmd, target_id_str, query, reply)