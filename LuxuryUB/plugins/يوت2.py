import os
import re
import asyncio
from yt_dlp import YoutubeDL
from telethon import events, Button
from LuxuryUB import luxur
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete

# --- الإعدادات والذاكرة المؤقتة ---
YT_SEARCH_CACHE = {}  # {user_id: [نتائج_البحث]}
COOKIE_PATH = "cookies.txt"

# 🛡️ إذا عندك بروكسي خليه هنا، وإذا ماكو خليه فارغ ""
MY_PROXY = "" 

# إعدادات البحث (لجلب المعلومات بس)
YDL_OPTIONS = {
    "format": "b/w", # أي صيغة المهم يجيب الداتا
    "quiet": True,
    "cookiefile": COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
    "proxy": MY_PROXY if MY_PROXY else None,
    "default_search": "ytsearch",
    "extractor_args": {"youtube": {"player_client": ["ios", "web"]}},
}

# --- دوال مساعدة لترتيب الشكل ---
def get_yt_buttons(index, video_id, total):
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
    title = video.get("title")
    duration = video.get("duration_string", "غير معروف")
    views = video.get("view_count", 0)
    channel = video.get("uploader", "غير معروف")
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

    proc = await edit_or_reply(event, "**⇆ جاري البحث عن النتائج...**")
    user_id = event.sender_id
    
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            search_data = ydl.extract_info(f"ytsearch10:{query}", download=False)
            if not search_data or 'entries' not in search_data or not search_data['entries']:
                return await proc.edit("**❌ لم يتم العثور على نتائج.**")
            
            entries = search_data['entries']
            YT_SEARCH_CACHE[user_id] = entries
            video = entries[0]
            caption = format_yt_caption(video)
            buttons = get_yt_buttons(0, video['id'], len(entries))
            
            # الإرسال عبر البوت المساعد لضمان عمل الأزرار
            await event.client.tgbot.send_file(
                event.chat_id, video.get('thumbnail', 'https://i.imgur.com/7A2n2P6.png'), caption=caption, buttons=buttons
            )
            await proc.delete()

    except Exception as e:
        await proc.edit(f"**⚠️ خطأ في البحث:** `{str(e)}`")

# --- 2️⃣ معالج تقليب الصفحات (Assistant Bot Side) ---
@luxur.tgbot.on(events.CallbackQuery(data=re.compile(b"yt_page_(\d+)")))
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
    
    await event.edit(caption, file=video.get('thumbnail', 'https://i.imgur.com/7A2n2P6.png'), buttons=buttons)

# --- 3️⃣ معالج التحميل (Assistant Bot Side) ---
@luxur.tgbot.on(events.CallbackQuery(data=re.compile(b"ytdl_(a|v)_(.*)")))
async def on_yt_download(event):
    dl_type = event.data_match.group(1).decode() 
    video_id = event.data_match.group(2).decode()
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    await event.answer("💎 جاري التحميل... قد يستغرق بعض الوقت.", alert=False)
    proc = await event.reply("**📥 جاري التحميل من سيرفرات يوتيوب...**")
    
    # 🔓 إعدادات التحميل הפعلي (كسر قيود الصيغ)
    download_opts = {
        "format": "ba/b/wa/w" if dl_type == "a" else "b/w",
        "outtmpl": f"downloads/{video_id}.%(ext)s",
        "cookiefile": COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
        "proxy": MY_PROXY if MY_PROXY else None,
        "extractor_args": {"youtube": {"player_client": ["ios", "web"]}},
    }

    try:
        with YoutubeDL(download_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            await proc.edit("**📤 جاري الرفع إلى تيليجرام...**")
            
            # إرسال الملف المكتمل
            await event.client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"**✅ تم التحميل بنجاح ✓**\n`{info['title']}`",
                supports_streaming=True if dl_type == "v" else False
            )
            await proc.delete()
            
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        await proc.edit(f"**❌ فشل التحميل:**\n`{str(e)}`")