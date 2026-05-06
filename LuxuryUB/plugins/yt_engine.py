import os
import asyncio
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 1. إعدادات المحرك (Engine Config)
# ==========================================
COOKIE_PATH = "cookies.txt" # تأكد من رفع هذا الملف بجانب ملفات التشغيل الأساسية
DOWNLOAD_DIR = "downloads"

# إنشاء مجلد التحميلات إذا لم يكن موجوداً لتجنب أخطاء المسار
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# مسبح الخيوط (Thread Pool) لمنع تجميد السورس
# 5 عمال (Workers) كافية جداً لعدم استهلاك معالج السيرفر
executor = ThreadPoolExecutor(max_workers=5)

# ==========================================
# 2. الدوال المتزامنة (التي تنفذ العمل الفعلي)
# ==========================================

def _sync_fast_search(query):
    """عملية البحث السطحي (تُنفذ في خيط منفصل)"""
    opts = {
        'extract_flat': True, # استخراج سطحي بدون فحص عميق للروابط
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch10', # جلب 10 نتائج
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            return ydl.extract_info(query, download=False).get('entries', [])
        except Exception as e:
            print(f"[Engine] Search Error: {e}")
            return []

def _sync_secure_download(video_id, dl_type):
    """عملية التحميل المعقدة (تُنفذ في خيط منفصل)"""
    # تحديد العملاء لتخطي حظر يوتيوب بناءً على وجود الكوكيز
    attack_clients = ["web", "mweb", "tv_embedded", "ios", "android"] if os.path.exists(COOKIE_PATH) else ["ios", "tv_embedded", "android"]
    
    # تحديد الصيغة
    format_type = "bestaudio[ext=m4a]/best" if dl_type == "a" else "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"

    opts = {
        "format": format_type,
        "outtmpl": f"{DOWNLOAD_DIR}/{video_id}.%(ext)s",
        "extractor_args": {"youtube": {"player_client": attack_clients}},
        "javascript_engine": "deno", # تفعيل محرك Deno لتخطي حماية PO-Token
        "concurrent_fragment_downloads": 7, # تسريع التحميل
        "quiet": True,
        "no_warnings": True,
        "cookiefile": COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            print(f"[Engine] Starting download for: {video_id}")
            info = ydl.extract_info(video_id, download=True)
            file_path = ydl.prepare_filename(info)
            
            # حساب حجم الملف بالميغابايت بذكاء
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"[Engine] Download completed. Size: {file_size_mb:.2f} MB")
            
            # إرجاع مسار الملف وحجمه لكي يقرر الواجهة من سيرفع (البوت أم اليوزر)
            return file_path, file_size_mb
            
        except Exception as e:
            print(f"[Engine] Download Error: {e}")
            return None, 0

# ==========================================
# 3. الواجهة غير المتزامنة (Asynchronous API)
# ==========================================

async def yt_fast_search(query):
    """تغليف البحث ليعمل بشكل غير متزامن مع تيليجرام"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, _sync_fast_search, query)

async def yt_secure_download(video_id, dl_type="a"):
    """تغليف التحميل ليعمل بشكل غير متزامن مع تيليجرام"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _sync_secure_download, video_id, dl_type)