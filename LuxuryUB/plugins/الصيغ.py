import asyncio
import os
import re
import time
import requests
from PIL import Image
from telethon import events
from LuxuryUB.core.session import luxur
from ..Config import Config

plugin_category = "misc"

# إنشاء مجلد مؤقت للملفات حتى ما تصير هوسة بالاستضافة
temp_dir = "temp_media"
os.makedirs(temp_dir, exist_ok=True)

cancel_process = False

@luxur.ar_cmd(pattern=r"حفظ_المحتوى (.+)", command=("حفظ_المحتوى", plugin_category))
async def save_media(event):
    message_link = event.pattern_match.group(1)
    if not message_link:
        return await event.edit("**᯽︙ يرجى تحديد رابط الرسالة ⚠️**")
    
    await event.edit("**᯽︙ يجري حفظ الميديا.... ⏱**")
    try:
        if "/c/" in message_link:
            channel_id, message_id = re.search(r"t.me\/c\/(\d+)\/(\d+)", message_link).groups()
            channel_id = int(f"-100{channel_id}")
        else:
            channel_username, message_id = re.search(r"t.me\/([^\/]+)\/(\d+)", message_link).groups()
            entity = await luxur.get_entity(channel_username)
            channel_id = entity.id
    except Exception as e:
        return await event.edit(f"**᯽︙ حدث خطأ بالرابط:** `{str(e)}`")

    try:
        message = await luxur.get_messages(channel_id, ids=int(message_id))
        if not message or not (message.media or message.document):
            return await event.edit("**᯽︙ الرسالة لا تحتوي على ميديا قابلة للحفظ ⚠️**")
        
        file_path = await luxur.download_media(message, file=temp_dir)
        await luxur.send_file('me', file=file_path, caption=message.text or "")
        os.remove(file_path)
        await event.edit(f"**᯽︙ تم حفظ الميديا بنجاح، اذهب إلى (الرسائل المحفوظة) ✓**")
    except Exception as e:
        await event.edit(f"**᯽︙ حدث خطأ أثناء الحفظ:** `{str(e)}`")

@luxur.ar_cmd(pattern="تحويل صورة$", command=("تحويل صورة", plugin_category))
async def sticker_to_photo(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file:
        return await event.edit("**᯽︙ يرجى الرد على ملصق لتحويله إلى صورة ⚠️**")
    if reply.file.ext == ".tgs":
        return await event.edit("**᯽︙ عذراً، لا يمكن تحويل الملصقات المتحركة (tgs) حالياً!**")
        
    await event.edit("**᯽︙ جارِ التحويل إلى صورة... ⏱**")
    try:
        photo = await reply.download_media(file=f"{temp_dir}/photo.jpg")
        await event.client.send_file(event.chat_id, photo, reply_to=reply.id)
        os.remove(photo)
        await event.delete()
    except Exception as e:
        await event.edit(f"**᯽︙ حدث خطأ:** `{e}`")


@luxur.ar_cmd(pattern="تحويل ملصق$", command=("تحويل ملصق", plugin_category))
async def photo_to_sticker(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file:
        return await event.edit("**᯽︙ يرجى الرد على صورة لتحويلها إلى ملصق ⚠️**")
        
    await event.edit("**᯽︙ جارِ التحويل إلى ملصق... ⏱**")
    try:
        sticker = await reply.download_media(file=f"{temp_dir}/sticker.webp")
        await event.client.send_file(event.chat_id, sticker, reply_to=reply.id, force_document=False)
        os.remove(sticker)
        await event.delete()
    except Exception as e:
        await event.edit(f"**᯽︙ حدث خطأ:** `{e}`")

@luxur.ar_cmd(pattern=r"تحويل متحركة ?([0-9.]+)?$", command=("تحويل متحركة", plugin_category))
async def video_to_gif(event):
    reply = await event.get_reply_message()
    if not reply or not reply.video:
        return await event.edit("**᯽︙ يرجى الرد على فيديو لتحويله إلى متحركة ⚠️**")
        
    await event.edit("**᯽︙ جارِ التحويل إلى متحركة... ⏱**")
    try:
        video = await reply.download_media(file=f"{temp_dir}/video.mp4")
        await event.client.send_file(event.chat_id, video, reply_to=reply.id, as_gif=True)
        os.remove(video)
        await event.delete()
    except Exception as e:
        await event.edit(f"**᯽︙ حدث خطأ:** `{e}`")


@luxur.ar_cmd(pattern="تحويل (mp3|بصمة|voice)$", command=("تحويل", plugin_category))
async def convert_audio(event):
    if not event.reply_to_msg_id:
        return await event.edit("**᯽︙ يـجب الـرد على اي مـلف صوتي اولا ⚠️**")
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        return await event.edit("**᯽︙ يـجب الـرد على اي مـلف صوتي اولا ⚠️**")
        
    input_str = event.pattern_match.group(1)
    await event.edit("**᯽︙ يتـم التـحويل انتـظر قليـلا ⏱**")
    
    try:
        downloaded_file_name = await event.client.download_media(reply_message, file=temp_dir)
    except Exception as e:
        return await event.edit(f"**᯽︙ خطأ بالتحميل:** `{str(e)}`")
        
    await event.edit("**᯽︙ تم التحميل، جارِ المعالجة... ⏱**")
    new_required_file_name = f"{temp_dir}/{input_str}_{round(time.time())}"
    
    if input_str in ["بصمة", "voice"]:
        new_required_file_name += ".ogg" 
        command_to_run = ["ffmpeg", "-i", downloaded_file_name, "-map", "0:a", "-codec:a", "libopus", "-b:a", "100k", "-vbr", "on", new_required_file_name]
        voice_note = True
    else:
        new_required_file_name += ".mp3"
        command_to_run = ["ffmpeg", "-i", downloaded_file_name, "-vn", new_required_file_name]
        voice_note = False
        
    try:
        process = await asyncio.create_subprocess_exec(*command_to_run, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            err_msg = stderr.decode().strip()
            await event.edit(f"**᯽︙ فشل التحويل بسبب أداة ffmpeg:**\n`{err_msg}`")
            if os.path.exists(downloaded_file_name): os.remove(downloaded_file_name)
            return
    except FileNotFoundError:
        await event.edit("**᯽︙ أداة `ffmpeg` غير منصبة في هذه الاستضافة!**\nلذلك لا يمكنك استخدام أوامر تحويل الصوت.")
        if os.path.exists(downloaded_file_name): os.remove(downloaded_file_name)
        return

    if os.path.exists(downloaded_file_name):
        os.remove(downloaded_file_name)
        
    if os.path.exists(new_required_file_name):
        await event.client.send_file(event.chat_id, file=new_required_file_name, reply_to=reply_message.id, voice_note=voice_note)
        os.remove(new_required_file_name)
        await event.delete()

@luxur.ar_cmd(pattern="الغاء سيف$", command=("الغاء سيف", plugin_category))
async def cancel_save(event):
    global cancel_process
    cancel_process = True
    await event.edit("**᯽︙ تم إلغاء عملية حفظ الميديا 🛑**")


@luxur.ar_cmd(pattern="سيف(?: |$)(.*) (\d+)", command=("سيف", plugin_category))
async def batch_save(event):
    global cancel_process
    cancel_process = False
    channel_username = event.pattern_match.group(1)
    limit = int(event.pattern_match.group(2))
    
    if not channel_username:
        return await event.edit("**᯽︙ يجب تحديد معرف القناة!**")
        
    await event.edit(f"**᯽︙ جاري جلب {limit} رسالة من القناة... ⏱**")
    
    try:
        channel_entity = await luxur.get_entity(channel_username)
        messages = await luxur.get_messages(channel_entity, limit=limit)
    except Exception as e:
        return await event.edit(f"**᯽︙ حدث خطأ أثناء جلب الرسائل:** `{str(e)}`")

    count = 0
    for message in messages:
        if cancel_process:
            cancel_process = False
            return await event.edit(f"**᯽︙ تم إيقاف عملية الحفظ! (حُفظ {count} ملف) ✓**")
        try:
            if message.media:
                file_path = await message.download_media(file=temp_dir)
                if file_path:
                    await luxur.send_file("me", file=file_path)
                    os.remove(file_path)
                    count += 1
        except Exception:
            continue

    await event.edit(f"**᯽︙ تم حفظ {count} ملف ميديا بنجاح في الرسائل المحفوظة ✓**")


@luxur.ar_cmd(pattern=r"بنتيرست (.+)", command=("بنتيرست", plugin_category))
async def pinterestAljoker(event):
    pinterest_url = event.pattern_match.group(1).strip()
    await event.edit("**᯽︙ يتـم جـلـب الـصـورة مـن بـنـتـريـست، انتـظر قليلا... ⏱**")
    
    # إضافة رؤوس (Headers) لخدع الموقع
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
    
    try:
        response = requests.get(pinterest_url, headers=headers, timeout=10)
        content_type = response.headers.get('content-type', '')

        # إذا كان الرابط مباشر لصورة
        if 'image' in content_type:
            img_data = response.content
        # إذا كان الرابط لصفحة (Pin)، نبحث عن رابط الصورة في الكود
        else:
            # البحث عن رابط الصورة الأصلي داخل كود الصفحة (Meta Tags)
            re_image = re.search(r'property="og:image" content="([^"]+)"', response.text)
            if re_image:
                img_url = re_image.group(1)
                img_data = requests.get(img_url, headers=headers).content
            else:
                return await event.edit("**᯽︙ فشل العثور على الصورة في هذا الرابط ⚠️**")

        # حفظ وإرسال الصورة
        img_path = f"{temp_dir}/pin_{round(time.time())}.jpg"
        with open(img_path, 'wb') as f:
            f.write(img_data)
            
        await event.client.send_file(event.chat_id, img_path, reply_to=event.reply_to_msg_id)
        os.remove(img_path)
        await event.delete()

    except Exception as e:
        await event.edit(f"**᯽︙ حـدث خـطـأ أثناء الجلب:** `{str(e)}`")