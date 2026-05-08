import subprocess
import sys
import os
import urllib.request
import zipfile
import json
import time

PACKAGES = [
    "telethon", "psycopg2-binary==2.9.9", "Pillow", "pydub",
    "SQLAlchemy==1.4.46", "aiohttp==3.9.5", "ocrspace", "ShazamAPI",
    "setuptools", "wheel", "cloudscraper", "speechrecognition", "colour",
    "qrcode", "python-barcode", "glitch_this", "cryptg",
    "beautifulsoup4", "cryptography", "moviepy==1.0.3",
    "pyquery", "tswift", "wikipedia", "fontTools", "emoji==2.12.1",
    "geopy", "gitpython", "gsearch", "gtts", "hachoir", "html-telegraph-poster",
    "humanize", "justwatch", "kwot", "lottie", "jikanpy", "lyricsgenius",
    "markdown", "motor", "patool", "prettytable", "psutil", "pyfiglet",
    "programmingquotes", "pygments", "pylast", "pymediainfo",
    "pySmartDL", "pytuneteller", "pytz", "wget", "urlextract", "search-engine-parser",
    "spamwatch", "speedtest-cli", "sqlalchemy-json", "telegraph", "tgcrypto",
    "validators", "vcsi", "ipaddress", "ujson==5.8.0", "randomstuff.py",
    "git+https://github.com/redaiq90/py-googletrans",
    "youtube-search-python", "ntgcalls==2.2.1b3",
    "git+https://github.com/pytgcalls/pytgcalls", "av==12.3.0"
]

SYSTEM_PACKAGES = {"setuptools", "wheel", "pip"}

GIT_PACKAGE_NAMES = {
    "git+https://github.com/redaiq90/py-googletrans": "googletrans",
    "git+https://github.com/pytgcalls/pytgcalls":      "py-tgcalls", 
}

GIT_LOCK_FILE = ".git_packages_installed"

REAL_NAMES = {
    "pillow":                 "pillow",
    "psycopg2-binary":        "psycopg2-binary",
    "sqlalchemy":             "sqlalchemy",
    "beautifulsoup4":         "beautifulsoup4",
    "speechrecognition":      "speechrecognition",
    "python-barcode":         "python-barcode",
    "html-telegraph-poster":  "html-telegraph-poster",
    "randomstuff.py":         "randomstuff.py",
    "search-engine-parser":   "search-engine-parser",
    "speedtest-cli":          "speedtest-cli",
    "youtube-search-python":  "youtube-search-python",
    "gitpython":              "gitpython",
    "fonttools":              "fonttools",
    "ntgcalls":               "ntgcalls",
}


def parse_requirement(pkg: str):
    if pkg.startswith("git+"):
        name = GIT_PACKAGE_NAMES.get(pkg, pkg.split("/")[-1].replace(".git", ""))
        return name, None, True  
    for sep in ("==", ">=", "<=", "!=", "~="):
        if sep in pkg:
            name, ver = pkg.split(sep, 1)
            return name.strip().lower(), ver.strip(), False
    return pkg.strip().lower(), None, False


def get_installed_packages() -> dict:
    local_site = os.path.abspath(".local/lib/python3.11/site-packages")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + ":" + local_site + ":" + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True, text=True, env=env
    )

    if result.returncode != 0 or not result.stdout.strip():
        return {}

    try:
        pkgs = json.loads(result.stdout)
        return {p["name"].lower(): p["version"] for p in pkgs}
    except Exception:
        return {}


def load_git_lock() -> set:
    """اقرأ مكتبات git اللي انتصبت مسبقاً"""
    if os.path.exists(GIT_LOCK_FILE):
        try:
            with open(GIT_LOCK_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_git_lock(git_urls: list):
    """احفظ مكتبات git بعد تثبيتها"""
    existing = load_git_lock()
    existing.update(git_urls)
    with open(GIT_LOCK_FILE, "w") as f:
        json.dump(list(existing), f)


def check_and_install():
    print("\n--- فحص المكتبات ---")
    t_start = time.time()

    print("[..] جاري قراءة المكتبات المنصبة...")
    installed    = get_installed_packages()
    git_locked   = load_git_lock()   
    t_fetch      = time.time() - t_start
    print(f"[OK] قُرئت {len(installed)} مكتبة في {t_fetch:.2f} ثانية")

    to_install   = []
    to_upgrade   = []
    git_to_install = []

    for pkg in PACKAGES:
        name_raw, required_ver, is_git = parse_requirement(pkg)

        if name_raw in SYSTEM_PACKAGES:
            continue

        if is_git:
            if pkg not in git_locked:
                git_to_install.append(pkg)
            continue

        name_lookup = REAL_NAMES.get(name_raw, name_raw).lower()
        current_ver = installed.get(name_lookup) or installed.get(name_raw)

        if current_ver is None:
            to_install.append(pkg)
        elif required_ver and current_ver != required_ver:
            to_upgrade.append((pkg, name_raw, current_ver, required_ver))

    t_compare = time.time() - t_start
    print(f"[OK] انتهت المقارنة في {t_compare:.2f} ثانية")

    all_normal = to_install + [item[0] for item in to_upgrade]

    if not all_normal and not git_to_install:
        print(f"[OK] كل المكتبات جاهزة! ({t_compare:.1f} ثانية)\n")
        return

    if to_install:
        print(f"\n[!!] مكتبات ناقصة ({len(to_install)}):")
        for p in to_install:
            print(f"     - {p}")

    if to_upgrade:
        print(f"\n[!!] مكتبات تحتاج تحديث ({len(to_upgrade)}):")
        for _, name, cur, req in to_upgrade:
            print(f"     - {name}: {cur} -> {req}")

    if git_to_install:
        print(f"\n[!!] مكتبات git غير منصبة ({len(git_to_install)}):")
        for p in git_to_install:
            print(f"     - {p}")

    tmp_dir = os.path.join(os.getcwd(), "tmp_pip")
    os.makedirs(tmp_dir, exist_ok=True)
    os.environ["TMPDIR"] = tmp_dir
    os.environ["TEMP"]   = tmp_dir
    os.environ["TMP"]    = tmp_dir

    if all_normal:
        batch_size = 21
        total = (len(all_normal) - 1) // batch_size + 1
        for i in range(0, len(all_normal), batch_size):
            batch     = all_normal[i:i + batch_size]
            batch_num = i // batch_size + 1
            print(f"\n-> تثبيت المجموعة {batch_num}/{total}...")
            cmd = [
                sys.executable, "-m", "pip", "install", *batch,
                "--no-cache-dir", "--disable-pip-version-check",
                "--prefer-binary", "--prefix", ".local", "--quiet"
            ]
            try:
                subprocess.call(cmd)
            except Exception as e:
                print(f"[!!] خطأ: {e}")

    if git_to_install:
        print(f"\n-> تثبيت مكتبات git ({len(git_to_install)})...")
        cmd = [
            sys.executable, "-m", "pip", "install", *git_to_install,
            "--no-cache-dir", "--disable-pip-version-check",
            "--prefix", ".local", "--quiet"
        ]
        try:
            ret = subprocess.call(cmd)
            if ret == 0:
                save_git_lock(git_to_install)
                print("[OK] تم حفظ مكتبات git في ملف القفل")
        except Exception as e:
            print(f"[!!] خطأ git: {e}")

    t_total = time.time() - t_start
    print(f"\n[OK] اكتمل في {t_total:.1f} ثانية")



if __name__ == "__main__":

    check_and_install()

    ytdlp_lock = ".ytdlp_ts"
    needs_update = (
        not os.path.exists(ytdlp_lock) or
        (time.time() - os.path.getmtime(ytdlp_lock)) > 86400
    )
    if needs_update:
        print("\n--- تحديث yt-dlp ---")
        os.system(
            f"{sys.executable} -m pip install --prefix .local -U --pre "
            f"'yt-dlp[default]' --quiet --disable-pip-version-check"
        )
        open(ytdlp_lock, "w").close()
    else:
        print("[OK] yt-dlp محدثة")

    deno_path = "./deno"
    if not os.path.exists(deno_path):
        print("\n--- تحميل Deno ---")
        try:
            url = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip"
            urllib.request.urlretrieve(url, "deno.zip")
            with zipfile.ZipFile("deno.zip", "r") as zf:
                zf.extractall(".")
            os.remove("deno.zip")
            os.chmod(deno_path, 0o755)
            print("[OK] تم تنصيب Deno!")
        except Exception as e:
            print(f"[!!] فشل Deno: {e}")

    config_path = "config.py"
    if not os.path.exists(config_path):
        print("\n--- اعدادات البوت (مرة واحدة) ---")
        print("ادخل كود الجلسة")
        session   = input("(STRING_SESSION): ")
        print("ادخل توكن البوت")
        bot_token = input("(TG_BOT_TOKEN): ")
        print("ادخل يوزر البوت")
        busername = input("(TG_BOT_USERNAME): ")
        print("ادخل الايدي مالتك")
        owner_id  = input("(OWNER_ID): ")

        config_content = f"""from sample_config import Config

class Development(Config):
    APP_ID = 27296905
    API_HASH = "d904b87c18da7611dd1dd554867b0b8f"
    ALIVE_NAME = "Luxury User"
    DB_URI = "sqlite:///luxury.db"
    STRING_SESSION = "{session}"
    TG_BOT_TOKEN = "{bot_token}"
    TG_BOT_USERNAME = "{busername}"
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

    print("\n--- جاري تشغيل لوكـجوري ---")
    local_path = os.path.abspath(".local/lib/python3.11/site-packages")
    os.environ["PYTHONPATH"] = (
        os.getcwd() + ":" + local_path + ":" + os.environ.get("PYTHONPATH", "")
    )
    os.system(f"{sys.executable} -m LuxuryUB")
