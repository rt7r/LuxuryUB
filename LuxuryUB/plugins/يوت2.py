import os
import re
import asyncio
from yt_dlp import YoutubeDL
from telethon import events, Button
from LuxuryUB import luxur, JEPVERSION
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete

# --- الإعدادات والذاكرة المؤقتة ---
YT_SEARCH_CACHE = {}  # {user_id: [نتائج_البحث]}
COOKIE_PATH = "luxury_cookies.txt"

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "cookiefile": COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
    "extractor_args": {"youtube": {"player_client": ["android"]}}, # محاكاة أندرويد لتخطي الحظر
}

# --- دوال مساعدة لترتيب الشكل ---
def get_yt_buttons(index, video_id, total):
    """صناعة الأزرار الشفافة مع الأسهم والتحميل"""
    return [
        [
            Button.inline("⬅️ السابق", data=f"yt_page_{index-1}"),
            Button.inline(f"📄 {index+1} / {total}", data="yt_info"),
            Button.inline("التالي ➡️", data=f"yt_page_{index+1}")
        ],
        [
            Button.inline("🎵 تحميل صوت", data=f"ytdl_a_{video_id}"),
            Button.inline("📜 القائمة", data="yt_list"),
            Button.inline("🎬 تحميل فيديو", data=f"ytdl_v_{video_id}")
        ]
    ]

def format_yt_caption(video):
    """تنسيق نص الرسالة مثل الصور المطلوبة"""
    title = video.get("title")
    duration = video.get("duration_string")
    views = video.get("view_count", 0)
    channel = video.get("uploader")
    return (
        f"**{title}**\n\n"
        f"**👤 القناة :** `{channel}`\n"
        f"**⏱️ المدة :** `{duration}`\n"
        f"**👁️ المشاهدات :** `{views:,}`\n\n"
        f"**💎 سـورس لوكـجوري ✓**"
    )

# --- 1️⃣ أمر البحث (UserBot Side) ---
@luxur.ar_cmd(pattern="(يوتيوب)(?:\s|$)([\s\S]*)")
async def luxury_yt_search(event):
    query = event.pattern_match.group(2)
    if not query:
        return await edit_delete(event, "**💎 يرجى كتابة اسم الفيديو للبحث.**")

    proc = await edit_or_reply(event, "**⇆ جاري البحث عن أفضل 10 نتائج...**")
    user_id = event.sender_id
    
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            search_data = ydl.extract_info(f"ytsearch10:{query}", download=False)["entries"]
            if not search_data:
                return await proc.edit("**❌ لم يتم العثور على نتائج.**")
            
            YT_SEARCH_CACHE[user_id] = search_data
            video = search_data[0]
            caption = format_yt_caption(video)
            buttons = get_yt_buttons(0, video['id'], len(search_data))
            
            # الإرسال عبر البوت المساعد لضمان عمل الأزرار
            await event.client.send_file(
                event.chat_id, video['thumbnail'], caption=caption, buttons=buttons
            )
            await proc.delete()

    except Exception as e:
        await proc.edit(f"**⚠️ خطأ في البحث:** `{str(e)}`")

# --- 2️⃣ معالج تقليب الصفحات (Assistant Bot Side) ---
@luxur.tg_bot.on(events.CallbackQuery(data=re.compile(b"yt_page_(\d+)")))
async def on_yt_page_change(event):
    page_index = int(event.data_match.group(1).decode())
    user_id = event.sender_id 
    
    if user_id not in YT_SEARCH_CACHE:
        return await event.answer("⚠️ انتهت جلسة البحث، ابحث من جديد.", alert=True)
    
    results = YT_SEARCH_CACHE[user_id]
    if page_index < 0 or page_index >= len(results):
        return await event.answer("🚫 لا توجد نتائج أخرى.")

    video = results[page_index]
    caption = format_yt_caption(video)
    buttons = get_yt_buttons(page_index, video['id'], len(results))
    
    await event.edit(caption, file=video['thumbnail'], buttons=buttons)

# --- 3️⃣ معالج التحميل (Assistant Bot Side) ---
@luxur.tg_bot.on(events.CallbackQuery(data=re.compile(b"ytdl_(a|v)_(.*)")))
async def on_yt_download(event):
    dl_type = event.data_match.group(1).decode() # 'a' for audio, 'v' for video
    video_id = event.data_match.group(2).decode()
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    await event.answer("💎 جاري التحميل... قد يستغرق ذلك وقتاً حسب حجم الملف.", alert=False)
    
    # إعدادات التحميل الفعلي
    download_opts = {
        "format": "bestaudio/best" if dl_type == "a" else "best",
        "outtmpl": f"downloads/{video_id}.%(ext)s",
        "cookiefile": COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }

    try:
        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # إرسال الملف المكتمل
            await event.client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"**✅ تم التحميل بنجاح ✓**\n`{info['title']}`",
                supports_streaming=True if dl_type == "v" else False
            )
            # تنظيف الملف بعد الإرسال لتوفير المساحة
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        await event.reply(f"**❌ فشل التحميل:** `{str(e)}`")