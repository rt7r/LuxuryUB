import os
import asyncio
import yt_dlp
import time
from ShazamAPI import Shazam
from telethon import events, types
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from JoKeRUB import l313l
from ..core.managers import edit_or_reply, edit_delete

DL_PATH = "downloads/"
if not os.path.exists(DL_PATH): os.makedirs(DL_PATH)

# =========================================================
async def fetch_video_only(client, bot_username, query):
    await client(UnblockRequest(bot_username))
    sent = await client.send_message(bot_username, query)
    video_msg = None
    
    for _ in range(20):
        await asyncio.sleep(2)
        messages = await client.get_messages(bot_username, limit=5)
        for m in messages:
            if m.id > sent.id and m.media:
                if hasattr(m, 'video') and m.video:
                    video_msg = m
                    break
                elif hasattr(m, 'document') and m.document and "video" in (m.document.mime_type or ""):
                    video_msg = m
                    break
        if video_msg:
            break
            
    try:
        await client(DeleteHistoryRequest(peer=bot_username, max_id=0, just_clear=True, revoke=True))
    except:
        pass
        
    return video_msg

async def fetch_audio_only(client, bot_username, query):
    await client(UnblockRequest(bot_username))
    sent = await client.send_message(bot_username, query)
    audio_msg = None
    for _ in range(15):
        await asyncio.sleep(2)
        messages = await client.get_messages(bot_username, limit=5)
        for m in messages:
            if m.id > sent.id and m.media and not isinstance(m.media, types.MessageMediaWebPage):
                if hasattr(m, 'audio') or (hasattr(m, 'document') and "audio" in (m.document.mime_type or "")):
                    audio_msg = m
                    break
        if audio_msg: break
    try:
        await client(DeleteHistoryRequest(peer=bot_username, max_id=0, just_clear=True, revoke=True))
    except: pass
    return audio_msg

# =========================================================

@l313l.ar_cmd(pattern="انستا(?:\s|$)([\s\S]*)")
async def dl_insta(event):
    link = event.pattern_match.group(1).strip()
    if not link: return await edit_or_reply(event, "**᯽︙ ضـع رابط الانستغرام مع الأمر ⚠️**")
    msg = await edit_or_reply(event, "**᯽︙ جـارِ جلب الفيديو من انستغرام... 📥**")
    media = await fetch_video_only(event.client, "@instasavegrambot", link)
    if media:
        await event.client.send_file(event.chat_id, media.media, caption="**✅ Instagram Video**", reply_to=event.reply_to_msg_id)
        await msg.delete()
    else:
        await msg.edit("**❌ فشل! لم يتم العثور على فيديو (تأكد أن الحساب عام).**")

@l313l.ar_cmd(pattern="(تيك|تك)(?:\s|$)([\s\S]*)")
async def dl_tiktok(event):
    link = event.pattern_match.group(2).strip()
    if not link: return await edit_or_reply(event, "**᯽︙ ضـع رابط التيك توك مع الأمر ⚠️**")
    msg = await edit_or_reply(event, "**᯽︙ جـارِ جلب فيديو التيك توك... 📥**")
    media = await fetch_video_only(event.client, "@ttsavebot", link)
    if media:
        await event.client.send_file(event.chat_id, media.media, caption="**✅ TikTok Video**", reply_to=event.reply_to_msg_id)
        await msg.delete()
    else:
        await msg.edit("**❌ فشل! البوت لم يرسل فيديو (قد يكون المنشور صورا فقط).**")

@l313l.ar_cmd(pattern="ستوري(?:\s|$)([\s\S]*)")
async def dl_story(event):
    # الميزة معطلة بناءً على طلبك
    await edit_or_reply(event, "**᯽︙ عذراً، ميزة الستوري غير متاحة حالياً ⚠️**")

@l313l.ar_cmd(pattern="(بحث|يوت)(?:\s|$)([\s\S]*)")
async def dl_youtube_search(event):
    query = event.pattern_match.group(2).strip()
    if not query: return await edit_or_reply(event, "**᯽︙ اكتب اسم الأغنية مع الأمر ⚠️**")
    msg = await edit_or_reply(event, "**᯽︙ جـارِ جلب الملف الصوتي... 📥**")
    media = await fetch_audio_only(event.client, "@GoldnB7Rbot", f"يوت {query}")
    if media:
        await event.client.send_file(event.chat_id, media.media, caption="**✅ تـم التحميل بنجاح 🎵**", reply_to=event.reply_to_msg_id)
        await msg.delete()
    else:
        await msg.edit("**❌ لم يتم العثور على نتائج.**")

# =========================================================

@l313l.ar_cmd(pattern="(تحميل ص|صوت|فيديو)(?:\s|$)([\s\S]*)")
async def dl_local_direct(event):
    cmd = event.pattern_match.group(1)
    query = event.pattern_match.group(2).strip()
    if not query: return await edit_or_reply(event, "**᯽︙ ضع الرابط مع الأمر ⚠️**")
    
    # يوتيوب يمر عبر البوت الخارجي
    if "youtube.com" in query or "youtu.be" in query:
        if cmd == "فيديو":
            msg = await edit_or_reply(event, "**᯽︙ جـارِ جلب الفيديو من يوتيوب... 📥**")
            media = await fetch_video_only(event.client, "@GoldnB7Rbot", f"فيديو {query}")
        else:
            msg = await edit_or_reply(event, "**᯽︙ جـارِ جلب الصوت من يوتيوب... 📥**")
            media = await fetch_audio_only(event.client, "@GoldnB7Rbot", f"يوت {query}")
            
        if media:
            await event.client.send_file(event.chat_id, media.media, caption="**✅ Done**", reply_to=event.reply_to_msg_id)
            return await msg.delete()
        return await msg.edit("**❌ فشل الجلب.**")

    msg = await edit_or_reply(event, "**᯽︙ جـارِ التحميل المباشر... 📥**")
    mode = "audio" if cmd in ["تحميل ص", "صوت"] else "video"
    filename = f"local_{int(time.time())}"
    ydl_opts = {
        'format': 'bestaudio/best' if mode == "audio" else 'best[ext=mp4]/best',
        'outtmpl': f'{DL_PATH}{filename}.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}] if mode == "audio" else [],
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            actual_file = ydl.prepare_filename(info)
            if mode == "audio": actual_file = actual_file.rsplit('.', 1)[0] + ".mp3"
        await event.client.send_file(event.chat_id, actual_file, caption=f"**🎬 TITLE:** `{info.get('title', 'Unknown')}`")
        await msg.delete()
        if os.path.exists(actual_file): os.remove(actual_file)
    except Exception:
        await msg.edit(f"**❌ فشل التحميل المباشر.**")

# =========================================================
@l313l.ar_cmd(pattern="اسم الاغنية$")
async def shazam_it(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await edit_delete(event, "**᯽︙ رد على بصمة أو مقطع صوتي أولاً ⚠️**")
    
    msg = await edit_or_reply(event, "**᯽︙ جـارِ التعرف على المقطع... 🎤**")
    file = await event.client.download_media(reply, DL_PATH)
    
    try:
        shazam = Shazam(open(file, 'rb').read())
        recognize_generator = shazam.recognizeSong()
        track_info = next(recognize_generator)
        track = track_info[1]['track']
        
        # هنا مسموح بإرسال الصور (غلاف الأغنية)
        await event.client.send_file(
            event.chat_id, track['images']['background'], 
            caption=f"**᯽︙ تـم العثور على الأغنية ✅**\n\n**🎵 العنوان:** `{track['title']}`\n**👤 الفنان:** `{track['subtitle']}`",
            reply_to=reply
        )
        await msg.delete()
    except:
        await msg.edit("**❌ عذراً، لم أستطع التعرف على هذا المقطع.**")
    finally:
        if os.path.exists(file): os.remove(file)

# ميزة الخاص (صوت فقط)
@l313l.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def users_pm_search(event):
    if event.sender_id == event.client.uid: return 
    text = event.raw_text.strip()
    if text.startswith("بحث "):
        query = text.replace("بحث ", "", 1).strip()
        status = await event.reply("`╮ جـارِ البحث عـن الإغـنيةة ... 🎧╰`")
        media_msg = await fetch_audio_only(event.client, "@GoldnB7Rbot", f"يوت {query}")
        if media_msg:
            await event.client.send_file(event.chat_id, media_msg.media, caption=f"**• تـم العثور على طلبك 🎵**", reply_to=event.id)
            await status.delete()
        else: await status.edit("**❌ نعتذر، لم نجد نتائج.**")