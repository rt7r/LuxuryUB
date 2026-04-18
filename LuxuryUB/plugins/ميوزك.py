import os
import random
import asyncio
import re
from yt_dlp import YoutubeDL
from telethon import events, functions
from pytgcalls.group_call_factory import GroupCallFactory, MTProtoClientType
from LuxuryUB import luxur
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..sql_helper.globals import gvarstatus, addgvar


YDL_AUDIO_OPTS = {
    "format": "bestaudio/best", 
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "default_search": "ytsearch",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "m4a",
        "preferredquality": "320",
    }]
}

YDL_VIDEO_OPTS = {
    "format": "best", 
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "default_search": "ytsearch",
    "postprocessors": [{
        "key": "FFmpegVideoConvertor",
        "preferedformat": "mp4"
    }]
}

# ==================== الذاكرة المؤقتة (Smart Tracking) ====================
active_calls = {} 
is_playing = {} 
playlist = {} 
authorized_users = {} 

def is_music_enabled(owner_id):
    return gvarstatus(owner_id, "MUSIC_STATUS") == "true"

@luxur.ar_cmd(pattern="(تفعيل|تعطيل) الميوزك$")
async def toggle_music(event):
    owner_id = (await event.client.get_me()).id
    status = "true" if "تفعيل" in event.text else "false"
    addgvar(owner_id, "MUSIC_STATUS", status)
    await edit_or_reply(event, f"**💎 تم {'تفعيل' if status=='true' else 'تعطيل'} نظام الميوزك بنجاح ✓**")

@luxur.ar_cmd(pattern="دعوة(?:\s|$)([\s\S]*)")
async def invite_vc(event):
    reply = await event.get_reply_message()
    target = event.pattern_match.group(1).strip()
    if not target and not reply:
        return await edit_delete(event, "**⚠️ يرجى الرد على شخص أو كتابة معرفه للدعوة.**")
    user = reply.sender_id if reply else target
    proc = await edit_or_reply(event, "**💎 جاري إرسال الدعوة...**")
    try:
        full_chat = await event.client(functions.channels.GetFullChannelRequest(event.chat_id))
        call_obj = full_chat.full_chat.call
        if not call_obj:
            return await proc.edit("**⚠️ لا توجد مكالمة نشطة لدعوته إليها.**")
        await event.client(functions.phone.InviteToGroupCallRequest(call=call_obj, users=[user]))
        await proc.edit("**✅ تم إرسال الدعوة بنجاح.**")
    except Exception as e:
        await proc.edit(f"**❌ فشل إرسال الدعوة:** `{str(e)}`")

MUSIC_CMDS = "(شغل 1|شغل فيديو|شغل|تشغيل|فيديو 1|فيديو|انضمام|مغادرة|فتح مكالمة|اطفاء مكالمة|حالة المكالمة|تخطي|وكف مؤقتا|وكف|وقف|كمل|استمرار|ايقاف نهائي|ايقاف|قائمة التشغيل)"

async def process_music_command(event, cmd, target_id_str, query, reply):
    owner_id = (await event.client.get_me()).id
    if not is_music_enabled(owner_id): return await event.reply("**⚠️ نظام الميوزك معطل حالياً.**")

    chat_id = int(target_id_str) if target_id_str else event.chat_id
    if owner_id not in active_calls:
        active_calls[owner_id] = GroupCallFactory(event.client, MTProtoClientType.TELETHON).get_group_call()
    call = active_calls[owner_id]
    
    if cmd in ["فتح مكالمة"]:
        try:
            await event.client(functions.phone.CreateGroupCallRequest(peer=chat_id, random_id=random.randint(10000, 999999999)))
            return await event.reply(f"**✅ تم فتح المكالمة الصوتية.**")
        except: return await event.reply("**⚠️ المكالمة مفتوحة بالفعل.**")
            
    if cmd in ["اطفاء مكالمة"]:
        try:
            full_chat = await event.client(functions.channels.GetFullChannelRequest(chat_id))
            if full_chat.full_chat.call:
                await event.client(functions.phone.DiscardGroupCallRequest(call=full_chat.full_chat.call))
                is_playing[chat_id] = False
                if chat_id in playlist: playlist[chat_id].clear()
                return await event.reply(f"**❌ تم إنهاء المكالمة الصوتية.**")
            return await event.reply("**⚠️ لا توجد مكالمة نشطة.**")
        except Exception as e: return await event.reply(f"**❌ خطأ:** `{str(e)}`")

    if cmd in ["حالة المكالمة"]:
        try:
            full_chat = await event.client(functions.channels.GetFullChannelRequest(chat_id))
            if not full_chat.full_chat.call: return await event.reply("**⚠️ لا توجد مكالمة نشطة هنا.**")
            call_info = await event.client(functions.phone.GetGroupCallRequest(call=full_chat.full_chat.call, limit=1))
            return await event.reply(f"**📊 حالة المكالمة :**\n**العنوان:** `{call_info.call.title or 'لا يوجد'}`\n**المشاركين:** `{call_info.call.participants_count}`")
        except Exception as e: return await event.reply(f"**⚠️ خطأ:** `{str(e)}`")

    if cmd in ["انضمام"]:
        try:
            await call.join(chat_id)
            return await event.reply("**✅ تم تجهيز المكالمة الصوتية والانضمام.**")
        except Exception as e: return await event.reply(f"**⚠️ خطأ:** `{str(e)}`")

    if cmd in ["مغادرة"]:
        try:
            await call.stop()
            is_playing[chat_id] = False
            return await event.reply("**⏹️ تم مغادرة المكالمة.**")
        except: return await event.reply("**⚠️ الحساب ليس في المكالمة.**")

    if cmd in ["اوكف", "وكف", "وقف"]:
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
                if next_item["is_video"]: await call.start_video(next_item["url"], repeat=False)
                else: await call.start_audio(next_item["url"], repeat=False)
                is_playing[chat_id] = True
                return await event.reply(f"**⏭️ تم التخطي، يتم الآن تشغيل:** `{next_item['title']}`")
            except Exception as e: return await event.reply(f"**⚠️ خطأ:** `{str(e)}`")
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
        for i, item in enumerate(playlist[chat_id], 1): text += f"**{i}.** `{item['title']}`\n"
        return await event.reply(text)

    if cmd in ["شغل", "تشغيل", "شغل 1", "فيديو", "شغل فيديو", "فيديو 1"]:
        proc = await event.reply("**💎 جاري معالجة الطلب وبدء البث ...**")
        is_video = "فيديو" in cmd or (reply and reply.video)
        is_force = "1" in cmd 
        url_or_path = ""
        title = ""

        try:
            if reply and (reply.audio or reply.video or reply.voice):
                await proc.edit("**📥 جاري تحميل الملف للاستضافة...**") 
                url_or_path = await reply.download_media()
                title = "ملف مرفق 📁"
                if is_video:
                    await proc.edit("**⚙️ جاري تعديل دقة الفيديو ليتوافق مع المكالمة...**")
                    out_path = f"luxury_vid_{random.randint(1000, 99999)}.mp4"
                    ff_cmd = f'ffmpeg -y -i "{url_or_path}" -vf "scale=-2:480" -c:v libx264 -preset ultrafast -crf 28 -c:a copy "{out_path}"'
                    process = await asyncio.create_subprocess_shell(ff_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                    await process.communicate()
                    if os.path.exists(out_path):
                        try: os.remove(url_or_path) 
                        except: pass
                        url_or_path = out_path 
            elif query or (reply and reply.text):
                search_query = query or reply.text
                await proc.edit(f"**💎 جاري البحث واستخراج البيانات...**\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")
                opts = YDL_VIDEO_OPTS if is_video else YDL_AUDIO_OPTS
                
                with YoutubeDL(opts) as ydl:
                    if not search_query.startswith("http"): search_query = f"ytsearch1:{search_query}"
                    info = ydl.extract_info(search_query, download=False)
                    if info and 'entries' in info and info['entries']: info = info['entries'][0] 
                    if not info: return await proc.edit("**❌ لم يتم العثور على نتائج.**")
                    url_or_path = info.get("url")
                    title = info.get("title", "مقطع غير معروف")
            else:
                return await proc.edit("**⚠️ يرجى كتابة اسم الأغنية أو الرد على ملف.**")

            if not url_or_path: return await proc.edit("**❌ فشل في استخراج رابط البث.**")
            if is_force:
                if chat_id in playlist: playlist[chat_id].clear()
                is_playing[chat_id] = False 
            
            if is_playing.get(chat_id) and not is_force:
                if chat_id not in playlist: playlist[chat_id] = []
                playlist[chat_id].append({"title": title, "url": url_or_path, "is_video": is_video})
                return await proc.edit(f"**⏳ تمت الإضافة إلى قائمة التشغيل:**\n`{title}`\n**الترتيب في الطابور:** `{len(playlist[chat_id])}`")
            else:
                try:
                    await call.join(chat_id)
                    if is_video: await call.start_video(url_or_path, repeat=False)
                    else: await call.start_audio(url_or_path, repeat=False)
                    is_playing[chat_id] = True
                except Exception as e: return await proc.edit(f"**⚠️ فشل البث المباشر:** `{str(e)}`")
                return await proc.edit(f"**🎶 يتم الآن تشغيل:**\n`{title}`\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")

        except Exception as e:
            if "Sign in to confirm" in str(e):
                return await proc.edit("**❌ فشل بسبب حماية يوتيوب.**\n**السبب:** ملف `cookies.txt` المرفوع منتهي الصلاحية أو تم حظره.\n**الحل:** استخرج ملف كوكيز جديد بصيغة (Netscape) وارفعه للاستضافة.")
            return await proc.edit(f"**⚠️ خطأ:** `{str(e)}`")

@luxur.ar_cmd(pattern=f"{MUSIC_CMDS}(?: -id (-\d+|\d+))?(?:\s|$)([\s\S]*)")
async def owner_music_handler(event):
    cmd = event.pattern_match.group(1)
    target_id_str = event.pattern_match.group(2)
    query = event.pattern_match.group(3).strip() if event.pattern_match.group(3) else None
    reply = await event.get_reply_message()
    await process_music_command(event, cmd, target_id_str, query, reply)

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

@luxur.on(events.NewMessage(incoming=True))
async def operator_listener(event):
    owner_id = (await event.client.get_me()).id
    sender_id = event.sender_id
    if sender_id not in authorized_users.get(owner_id, set()): return
    text = event.raw_text.strip()
    match = re.match(f"^{MUSIC_CMDS}(?: -id (-\d+|\d+))?(?:\s|$)([\s\S]*)", text)
    if match:
        cmd = match.group(1)
        target_id_str = match.group(2)
        query = match.group(3).strip() if match.group(3) else None
        reply = await event.get_reply_message()
        if cmd in ["مغادرة", "ايقاف نهائي", "اطفاء مكالمة"]:
            return await event.reply("**⚠️ عذراً، لا تمتلك صلاحية لهذا الأمر.**")
        await process_music_command(event, cmd, target_id_str, query, reply)