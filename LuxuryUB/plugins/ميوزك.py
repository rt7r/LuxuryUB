import asyncio
import os
import random
from yt_dlp import YoutubeDL
from telethon import events, functions, types
from LuxuryUB import luxur
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..sql_helper.globals import gvarstatus, addgvar

# 🚀 تم تغيير الاستدعاءات لتتوافق وية النسخة الرسمية اللي نصبتها
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError

# 1. إعدادات يوتيوب للصوت فقط
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

# 2. إعدادات يوتيوب للفيديو
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

# الذاكرة المؤقتة للجلسات والمشغلين
active_calls = {} # {owner_id: call_app_instance}
authorized_users = {} # {owner_id: set(user_ids)}

# ⚙️ دالة لتهيئة محرك الاتصال الجديد وتخزينه
async def get_call_app(client, owner_id):
    if owner_id not in active_calls:
        app = PyTgCalls(client)
        await app.start()
        active_calls[owner_id] = app
    return active_calls[owner_id]

# ==================== دالة التحقق من الخدمة ====================
def is_music_enabled(owner_id):
    return gvarstatus(owner_id, "MUSIC_STATUS") == "true"

# ==================== أوامر التحكم بالخدمة ====================
@luxur.ar_cmd(pattern="(تفعيل|تعطيل) الميوزك$")
async def toggle_music(event):
    owner_id = (await event.client.get_me()).id
    status = "true" if "تفعيل" in event.text else "false"
    addgvar(owner_id, "MUSIC_STATUS", status)
    await edit_or_reply(event, f"**💎 تم {'تفعيل' if status=='true' else 'تعطيل'} نظام الميوزك بنجاح ✓**")

@luxur.ar_cmd(pattern="(شغل|تشغيل|فيديو|شغل فيديو)( \d+)?(?:\s|$)([\s\S]*)")
async def luxury_play(event):
    owner_id = (await event.client.get_me()).id
    if not is_music_enabled(owner_id):
        return await edit_delete(event, "**⚠️ نظام الميوزك معطل حالياً، قم بتفعيله أولاً.**")

    cmd = event.pattern_match.group(1)
    is_forced = bool(event.pattern_match.group(2)) 
    query = event.pattern_match.group(3)
    reply = await event.get_reply_message()
    
    chat_id = event.chat_id
    if query and " -id " in query:
        query, target_id = query.split(" -id ")
        chat_id = int(target_id.strip())

    proc = await edit_or_reply(event, "**💎 جاري معالجة الطلب وبدء البث ...**")
    
    # استدعاء المحرك الجديد
    call_app = await get_call_app(event.client, owner_id)
    is_video = "فيديو" in cmd or (reply and reply.video)
    
    try:
        # 1. التشغيل بالرد على ملف
        if reply and (reply.audio or reply.video or reply.voice):
            await proc.edit("**📥 جاري تحميل الملف للاستضافة لتشغيله...**") 
            path = await reply.download_media()
            
            media_stream = AudioVideoPiped(path) if is_video else AudioPiped(path)
            
            try:
                await call_app.join_group_call(chat_id, media_stream)
            except NoActiveGroupCall:
                await event.client(functions.phone.CreateGroupCallRequest(peer=chat_id, random_id=random.randint(10000, 999999999)))
                await asyncio.sleep(2)
                await call_app.join_group_call(chat_id, media_stream)
            except AlreadyJoinedError:
                await call_app.change_stream(chat_id, media_stream)
                
            return await proc.edit(f"**✅ تم تشغيل الملف المرفق بنجاح ✓**\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")

        # 2. التشغيل من يوتيوب (نص أو رابط)
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
                        return await proc.edit("**❌ لم يتم العثور على نتائج في يوتيوب.**")
                else:
                    info = ydl.extract_info(search_query, download=False)
                
                if not info:
                    return await proc.edit("**❌ فشل في جلب المقطع بسبب حماية يوتيوب.**")
                
                stream_url = info.get("url")
                title = info.get("title", "مقطع غير معروف")
            
            if not stream_url:
                 return await proc.edit("**❌ لم يتم العثور على رابط البث المباشر.**")

            media_stream = AudioVideoPiped(stream_url) if is_video else AudioPiped(stream_url)
            
            try:
                await call_app.join_group_call(chat_id, media_stream)
            except NoActiveGroupCall:
                await event.client(functions.phone.CreateGroupCallRequest(peer=chat_id, random_id=random.randint(10000, 999999999)))
                await asyncio.sleep(2)
                await call_app.join_group_call(chat_id, media_stream)
            except AlreadyJoinedError:
                await call_app.change_stream(chat_id, media_stream)
                
            return await proc.edit(f"**🎶 يتم الآن تشغيل :**\n`{title}`\n**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`")
            
        else:
             return await proc.edit("**⚠️ يرجى كتابة اسم الأغنية أو الرد على ملف صوتي/فيديو.**")

    except Exception as e:
        await proc.edit(f"**⚠️ خطأ:** `{str(e)}`")

@luxur.ar_cmd(pattern="(تخطي|وقف|اوكف|كمل|خروج|انضمام|مغادرة)(?:\s|$)([\s\S]*)")
async def music_controls(event):
    cmd = event.pattern_match.group(1)
    query = event.pattern_match.group(2)
    
    chat_id = event.chat_id
    if query and "-id " in query:
        chat_id = int(query.replace("-id ", "").strip())
    elif query and query.strip().replace("-", "").isdigit():
        chat_id = int(query.strip())

    owner_id = (await event.client.get_me()).id
    call_app = active_calls.get(owner_id)
    
    if cmd == "انضمام":
        return await edit_or_reply(event, "**⚠️ يرجى تشغيل مقطع للانضمام للمكالمة.**")

    if not call_app: return await edit_delete(event, "**⚠️ الحساب ليس في مكالمة حالياً.**")

    try:
        if cmd in ["وقف", "اوكف"]:
            await call_app.pause_stream(chat_id)
            await edit_or_reply(event, "**⏸️ تم إيقاف التشغيل مؤقتاً.**")
        elif cmd == "كمل":
            await call_app.resume_stream(chat_id)
            await edit_or_reply(event, "**▶️ تم استئناف التشغيل.**")
        elif cmd in ["مغادرة", "خروج"]:
            await call_app.leave_group_call(chat_id)
            await edit_or_reply(event, "**⏹️ تم مغادرة المكالمة.**")
        elif cmd == "تخطي":
            await edit_or_reply(event, "**⏭️ يتم تخطي المقطع الحالي ...**")
    except Exception as e:
        await edit_or_reply(event, f"**⚠️ حدث خطأ:** `{str(e)}`")


@luxur.ar_cmd(pattern="(فتح|اطفاء) مكالمة$")
async def call_manage(event):
    if "فتح" in event.text:
        try:
            await event.client(functions.phone.CreateGroupCallRequest(
                peer=event.chat_id,
                random_id=random.randint(10000, 999999999)
            ))
            await edit_or_reply(event, "**✅ تم فتح المكالمة الصوتية بنجاح.**")
        except Exception as e:
             await event.reply("**⚠️ المكالمة مفتوحة بالفعل.**")
    else:
        try:
            full_chat = await event.client(functions.channels.GetFullChannelRequest(event.chat_id))
            if full_chat.full_chat.call:
                await event.client(functions.phone.DiscardGroupCallRequest(call=full_chat.full_chat.call))
                await edit_or_reply(event, "**❌ تم إنهاء المكالمة الصوتية.**")
            else:
                await event.reply("**⚠️ لا توجد مكالمة نشطة لإنهائها.**")
        except Exception as e:
            await edit_or_reply(event, f"**❌ خطأ:** `{str(e)}`")

@luxur.ar_cmd(pattern="معلومات المكالمة$")
async def call_info(event):
    call = await event.client(functions.phone.GetGroupCallRequest(peer=event.chat_id))
    await edit_or_reply(event, f"**📊 معلومات المكالمة :**\n**العنوان:** `{call.call.title or 'لا يوجد'}`\n**المشاركين:** `{call.call.participants_count}`")

# ==================== إدارة المشغلين ====================
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

@luxur.ar_cmd(pattern="ايقاف$")
async def luxury_kill_media(event):
    owner_id = (await event.client.get_me()).id
    call_app = active_calls.get(owner_id)
    
    if not call_app:
        return await edit_delete(event, "**💎 الحساب ليس في مكالمة أصلاً.**")
    
    try:
        await call_app.leave_group_call(event.chat_id)
        await edit_or_reply(event, "**⏹️ تم إيقاف التشغيل وتصفير المشغل بنجاح ✓**\n*(تم الخروج من المكالمة)*")
    except Exception as e:
        await edit_or_reply(event, f"**⚠️ فشل الإيقاف:** `{str(e)}`")

@luxur.ar_cmd(pattern="تسمية ([\s\S]*)")
async def rename_call(event):
    new_title = event.pattern_match.group(1)
    if not new_title:
        return await edit_delete(event, "**💎 يرجى كتابة الاسم الجديد بعد الأمر.**")
    
    try:
        full_chat = await event.client(functions.channels.GetFullChannelRequest(event.chat_id))
        
        if not full_chat.full_chat.call:
            return await edit_or_reply(event, "**❌ لا توجد مكالمة نشطة حالياً لتغيير اسمها.**")
            
        await event.client(functions.phone.EditGroupCallTitleRequest(
            call=full_chat.full_chat.call, 
            title=new_title
        ))
        
        await edit_or_reply(event, f"**✅ تم تغيير اسم المكالمة إلى :** `{new_title}`")
        
    except Exception as e:
        await edit_or_reply(event, f"**❌ فشل تغيير الاسم:** `{str(e)}`")

# قائمة الكلمات المفتاحية للمشغلين
MUSIC_TRIGGERS = ["شغل", "تشغيل", "فيديو", "وقف", "اوكف", "كمل", "تخطي", "ايقاف", "مغادرة", "خروج"]

@luxur.on(events.NewMessage(incoming=True))
async def operators_listener(event):
    owner_id = (await event.client.get_me()).id
    sender_id = event.sender_id
    text = event.raw_text.strip()

    # 1. التحقق: هل الشخص مشغل مسموح له؟ (أو المالك نفسه)
    is_auth = sender_id in authorized_users.get(owner_id, set())
    if not is_auth and sender_id != owner_id:
        return

    # 2. التحقق: هل الكلمة تبدأ بأحد أوامر الميوزك؟
    trigger = next((t for t in MUSIC_TRIGGERS if text.startswith(t)), None)
    if not trigger:
        return

    # 3. توجيه الأمر للدالة المناسبة (بدون الحاجة لنقطة)
    if trigger in ["شغل", "تشغيل", "فيديو"]:
        query = text.replace(trigger, "").strip()
        event.pattern_match = type('Match', (object,), {'group': lambda i: query if i==3 else trigger})
        await luxury_play(event)
        
    elif trigger in ["وقف", "اوكف", "كمل", "تخطي", "ايقاف", "مغادرة", "خروج"]:
        event.pattern_match = type('Match', (object,), {'group': lambda i: trigger if i==1 else None})
        await music_controls(event)