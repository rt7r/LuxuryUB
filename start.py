import subprocess
import sys
import os

def install_first_time():
    packages = [
        "telethon", "psycopg2-binary==2.9.9", "Pillow", "pydub",
        "SQLAlchemy==1.4.46", "aiohttp==3.9.5", "ocrspace", "ShazamAPI", "selenium",
        "setuptools", "wheel", "cloudscraper", "speechrecognition", "colour",
        "qrcode", "python-barcode", "jotquote", "glitch_this", "cryptg",
        "cowpy", "beautifulsoup4", "cfscrape", "cryptography", "moviepy==1.0.3",
        "pyquery", "tswift", "wikipedia", "fontTools", "emoji==1.7.0",
        "geopy", "gitpython", "google-api-python-client", "google-auth-httplib2",
        "google-auth-oauthlib", "gsearch", "gtts", "hachoir", "html-telegraph-poster",
        "humanize", "justwatch", "kwot", "lottie", "jikanpy", "lyricsgenius",
        "markdown", "motor", "patool", "prettytable", "psutil", "pyfiglet",
        "PyGithub", "programmingquotes", "pygments", "pylast", "pymediainfo",
        "pySmartDL", "pytuneteller", "pytz", "wget", "urlextract", "search-engine-parser",
        "spamwatch", "speedtest-cli", "sqlalchemy-json", "telegraph", "tgcrypto",
        "validators", "vcsi", "ipaddress", "wand", "ujson==5.8.0", "randomstuff.py",
        "git+https://github.com/redaiq90/py-googletrans", "yt-dlp[default]", "youtube-search-python", 
        "pytgcalls==3.0.0.dev24", "av==12.3.0"
    ]
 
    print("--- بدء التثبيت المكاتب ---")

    tmp_dir = os.path.join(os.getcwd(), "tmp_pip")
    os.makedirs(tmp_dir, exist_ok=True)
    os.environ["TMPDIR"] = tmp_dir
    os.environ["TEMP"] = tmp_dir
    os.environ["TMP"] = tmp_dir
    
    batch_size = 25
    total_batches = (len(packages) // batch_size) + 1

    for i in range(0, len(packages), batch_size):
        batch = packages[i:i + batch_size]
        print(f"\n-> ⏳ جاري تثبيت المجموعة {(i // batch_size) + 1} من {total_batches}...")

        cmd = [
                  sys.executable, "-m", "pip", "install"
              ] + batch + [
                  "--no-cache-dir",
                  "--disable-pip-version-check",
                  "--prefer-binary",
                  "--prefix", ".local"
              ]

        try:
            subprocess.call(cmd)
        except Exception as e:
            print(f"تخطي خطأ بسيط في هذه المجموعة: {e}")

if __name__ == "__main__":
    install_first_time()

    os.system(f"{sys.executable} -m pip install --prefix .local -U --pre 'yt-dlp[default]'")

    config_path = "config.py"
    if not os.path.exists(config_path):
        print("\n--- 🔐 إعدادات البوت (لمرة واحدة فقط) ---")
        session = input("👤 أدخل كود الجلسة (STRING_SESSION): ")
        bot_token = input("🤖 أدخل توكن البوت (TG_BOT_TOKEN): ")
        owner_id = input("🆔 أدخل الآيدي مالتك (OWNER_ID): ")

        config_content = f"""from sample_config import Config

class Development(Config):
    APP_ID = 27296905
    API_HASH = "d904b87c18da7611dd1dd554867b0b8f"
    ALIVE_NAME = "Luxury User" 
    
    DB_URI = "sqlite:///luxury.db"

    STRING_SESSION = "{session}"
    TG_BOT_TOKEN = "{bot_token}"

    COMMAND_HAND_LER = "."
    SUDO_COMMAND_HAND_LER = "."

    OWNER_ID = {owner_id}
    SUDO_USERS = [{owner_id}, 1165225957] 

    UPSTREAM_REPO = "https://github.com/rt7r/LuxuryUB"
    UPSTREAM_BRANCH = "main"

    PRIVATE_GROUP_BOT_API_ID = 0
    PM_LOGGER_GROUP_ID = 0
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ تم إنشاء ملف config.py وحفظ معلوماتك بنجاح.")

    # 4. تشغيل السورس الأصلي
    print("\n--- ✅ اكتمل التثبيت.. جاري تشغيل لوكـجوري ---")
    local_path = os.path.abspath(".local/lib/python3.11/site-packages")
    os.environ['PYTHONPATH'] = os.getcwd() + ":" + local_path + ":" + os.environ.get('PYTHONPATH', '')
    os.system(f"{sys.executable} -m LuxuryUB")