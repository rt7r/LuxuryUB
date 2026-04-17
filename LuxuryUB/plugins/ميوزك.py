import asyncio
import os
import random
from yt_dlp import YoutubeDL
from pytgcalls import GroupCallFactory
from pytgcalls.exceptions import GroupCallNotFoundError
from telethon import events, functions, types
from LuxuryUB import luxur
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..sql_helper.globals import gvarstatus, addgvar
from pytgcalls.group_call_factory import MTProtoClientType

YDL_OPTIONS = {
    "format": "bestaudio/best", # يختار أفضل صوت متاح مهما كان نوعه
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    # 🛡️ أهم إضافة: تخطي حظر التوقيع (Signature) وتغيير المتصفح
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "logtostderr": False,
    "geo_bypass": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "extractor_args": {
        "youtube": {
            "player_client": ["web", "mweb"], # لغينا الأندرويد لأن يضرب الكوكيز
            "skip": ["dash", "hls"]
        }
    }
}
# الذاكرة المؤقتة للجلسات والمشغلين
active_calls = {} # {user_id: group_call_instance}
authorized_users = {} # {owner_id: set(user_ids)}

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

# ==================== أوامر التشغيل (صوت وفيديو) ====================
# تأكد إن هذا الاستدعاء موجود بداية الملف، إذا ماكو ضيفه ويه الاستدعاءات فوك
from pytgcalls.group_call_factory import MTProtoClientType

@luxur.ar_cmd(pattern="(شغل|تشغيل|فيديو|شغل فيديو)( \d+)?(?:\s|$)([\s\S]*)")
async def luxury_play(event):
    owner_id = (await event.client.get_me()).id
    if not is_music_enabled(owner_id):
        return await edit_delete(event, "**⚠️ نظام الميوزك معطل حالياً، قم بتفعيله أولاً.**")

    cmd = event.pattern_match.group(1)
    is_forced = bool(event.pattern_match.group(2)) # لشغل 1 وفيديو 1
    query = event.pattern_match.group(3)
    reply = await event.get_reply_message()
    
    chat_id = event.chat_id
    # منطق الـ ID الموحد
    if query and " -id " in query:
        query, target_id = query.split(" -id ")
        chat_id = int(target_id.strip())

    proc = await edit_or_reply(event, "**💎 جاري معالجة الطلب وبدء البث ...**")
    
    # 🛠️ التعديل المهم هنا: ضفنا (MTProtoClientType.TELETHON) حتى ما يطلب Pyrogram ويطفى
    if owner_id not in active_calls:
        active_calls[owner_id] = GroupCallFactory(event.client, MTProtoClientType.TELETHON).get_group_call()
    
    call = active_calls[owner_id]
    
    try:
        # 1. إذا كان التشغيل من يوتيوب (نص)
        if query or (reply and reply.text):
            search_query = query or reply.text
            with YoutubeDL(YDL_OPTIONS) as ydl:
                # راح نستخدم الكوكيز والفورمات الجديد اللي سويناه فوك
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)["entries"][0]
                url = info["url"]
                title = info["title"]
            
            await call.join(chat_id)
            if "فيديو" in cmd:
                await call.start_video(url, repeat=not is_forced)
            else:
                await call.start_audio(url, repeat=not is_forced)
            await proc.edit(f"**🎶 يتم الآن تشغيل :**\n`{title}`\n**نوع البث:** `{'فيديو 🎬' if 'فيديو' in cmd else 'صوت 🎵'}`")

        # 2. إذا كان التشغيل بالرد على ملف (ملف صوتي أو فيديو بالكروب)
        elif reply and (reply.audio or reply.video or reply.voice):
            await proc.edit("**📥 جاري تحميل الملف للاستضافة لتشغيله...**") # ضفتلك هذا حتى تعرف ديحمل
            path = await reply.download_media()
            await call.join(chat_id)
            if reply.video or "فيديو" in cmd:
                await call.start_video(path)
            else:
                await call.start_audio(path)
            await proc.edit(f"**✅ تم تشغيل الملف المرفق بنجاح ✓**")
            
        else:
             await proc.edit("**⚠️ يرجى كتابة اسم الأغنية أو الرد على ملف صوتي/فيديو.**")

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
    call = active_calls.get(owner_id)
    
    if cmd == "انضمام":
        if owner_id not in active_calls:
            active_calls[owner_id] = GroupCallFactory(event.client, MTProtoClientType.TELETHON).get_group_call()
        await active_calls[owner_id].join(chat_id)
        return await edit_or_reply(event, f"**✅ انضم الحساب للمكالمة في :** `{chat_id}`")

    if not call: return await edit_delete(event, "**⚠️ الحساب ليس في مكالمة حالياً.**")

    if cmd in ["وقف", "اوكف"]:
        await call.pause_play()
        await edit_or_reply(event, "**⏸️ تم إيقاف التشغيل مؤقتاً.**")
    elif cmd == "كمل":
        await call.resume_play()
        await edit_or_reply(event, "**▶️ تم استئناف التشغيل.**")
    elif cmd in ["مغادرة", "خروج"]:
        await call.stop()
        del active_calls[owner_id]
        await edit_or_reply(event, "**⏹️ تم مغادرة المكالمة.**")
    elif cmd == "تخطي":
        await edit_or_reply(event, "**⏭️ يتم تخطي المقطع الحالي ...**")

@luxur.ar_cmd(pattern="(فتح|اطفاء) مكالمة$")
async def call_manage(event):
    if "فتح" in event.text:
        try:
            # فتح المكالمة (ضفنا random_id لأن تليثون يطلبه مرات حتى ما يضرب ايرور)
            await event.client(functions.phone.CreateGroupCallRequest(
                peer=event.chat_id,
                random_id=random.randint(10000, 999999999)
            ))
            await edit_or_reply(event, "**✅ تم فتح المكالمة الصوتية بنجاح.**")
        except Exception as e:
             await event.reply("**⚠️ المكالمة مفتوحة بالفعل.**")
    else:
        try:
            # 1. نجيب معلومات الكروب بالبداية
            full_chat = await event.client(functions.channels.GetFullChannelRequest(event.chat_id))
            
            # 2. نتحقق إذا اكو مكالمة أصلاً حتى ننهيها
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
    call = active_calls.get(owner_id)
    
    if not call:
        return await edit_delete(event, "**💎 الحساب ليس في مكالمة أصلاً.**")
    
    try:
        # إيقاف البث الصوتي والمرئي نهائياً
        await call.stop_audio()
        await call.stop_video()
        await edit_or_reply(event, "**⏹️ تم إيقاف التشغيل وتصفير المشغل بنجاح ✓**\n*(الحساب لا يزال في المكالمة)*")
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
        # هنا نستدعي دالة التشغيل ونمرر لها النص بعد كلمة "شغل"
        query = text.replace(trigger, "").strip()
        event.pattern_match = type('Match', (object,), {'group': lambda i: query if i==3 else trigger})
        await luxury_play(event)
        
    elif trigger in ["وقف", "اوكف", "كمل", "تخطي", "ايقاف", "مغادرة", "خروج"]:
        # توجيه لأوامر التحكم
        event.pattern_match = type('Match', (object,), {'group': lambda i: trigger if i==1 else None})
        await music_controls(event)