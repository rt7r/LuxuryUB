import asyncio
import os
import contextlib
import sys
import requests
import heroku3
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from telethon import events 

from LuxuryUB import luxur, HEROKU_APP, StartTime
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply

# إعدادات السجل
LOGS = logging.getLogger(__name__)
plugin_category = "tools"

# --- ثوابت التحديث (Luxury Style) ---
HEROKU_APP_NAME = Config.HEROKU_APP_NAME or None
HEROKU_API_KEY = Config.HEROKU_API_KEY or None
UPSTREAM_REPO_URL = "https://github.com/rt7r/LuxuryUB" 
UPSTREAM_REPO_BRANCH = "main"

# قائمة المطورين المسموح لهم بالتحديث الإجباري (أنت فقط)
progs = [1165225957] # آيديك وآيدي مطور السورس الأساسي

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- دوال مساعدة ---

async def gen_chlog(repo, diff):
    """توليد قائمة التغييرات البرمجية"""
    d_form = "%d/%m/%y"
    return "".join(
        f" • {c.message} {c.author}\n ({c.committed_datetime.strftime(d_form)}) "
        for c in repo.iter_commits(diff)
    )

async def update_requirements():
    """تحديث مكتبات السورس"""
    reqs = "requirements.txt"
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs, "--upgrade", "--force-reinstall"]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)

async def deploy(event, repo, ups_rem, ac_br):
    """تحديث خاص ببيئة هيروكو"""
    if not HEROKU_API_KEY or not HEROKU_APP_NAME:
        return await event.edit("**❌ خطأ: بيانات هيروكو غير مكتملة في الفارات.**")
    
    await event.edit("**᯽︙ جاري تحديث ريبو التنصيب لـ لوكجوري، انتظر 5 دقائق...**")
    
    ups_rem.fetch(ac_br)
    repo.git.reset("--hard", "FETCH_HEAD")
    heroku = heroku3.from_key(HEROKU_API_KEY)
    heroku_app = heroku.app(HEROKU_APP_NAME)
    
    heroku_git_url = heroku_app.git_url.replace("https://", f"https://api:{HEROKU_API_KEY}@")
    
    if "heroku" in repo.remotes:
        remote = repo.remote("heroku")
        remote.set_url(heroku_git_url)
    else:
        remote = repo.create_remote("heroku", heroku_git_url)
    
    try:
        remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        await event.edit("**✅ تم إرسال التحديث لهيروكو، جاري إعادة بناء السورس...**")
        if HEROKU_APP:
            HEROKU_APP.restart()
    except Exception as e:
        await event.edit(f"**❌ حدث خطأ في هيروكو:**\n`{str(e)}`")

# --- الأوامر الرئيسية ---

@luxur.ar_cmd(
    pattern="تحديث(| الان)?$",
    command=("تحديث", plugin_category),
    info={
        "header": "لـ تحديث سورس لوكجوري.",
        "usage": ["{tr}تحديث", "{tr}تحديث الان"],
    },
)
async def upstream(event):
    if event.sender_id != Config.OWNER_ID:
        return await edit_or_reply(event, "**❌ عذراً، أمر التحديث مخصص للمالك الأساسي للسورس فقط للحفاظ على استقرار السيرفر.**")
        
    conf = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
    event = await edit_or_reply(event, "**᯽︙ جاري البحث عن تحديثات لـ LuxuryUB...**")
    
    try:
        repo = Repo()
    except (NoSuchPathError, InvalidGitRepositoryError):
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO_URL)
        origin.fetch()
        repo.create_head(UPSTREAM_REPO_BRANCH, origin.refs[UPSTREAM_REPO_BRANCH])
        repo.heads[UPSTREAM_REPO_BRANCH].checkout(True)

    try:
        ups_rem = repo.remote("upstream")
    except ValueError:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO_URL)
    
    ups_rem.fetch(UPSTREAM_REPO_BRANCH)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{UPSTREAM_REPO_BRANCH}")

    if not changelog:
        return await event.edit("**᯽︙ سورس لوكجوري محدث إلى آخر إصدار ✓**")

    if conf != "الان":
        msg = f"**᯽︙ تحديث جديد متوفر لسورس لوكجوري**\n\n**📝 التغييرات:**\n{changelog}\n\n**💡 للتحديث ارسل :** `.تحديث الان`"
        return await event.edit(msg)

    await event.edit("**᯽︙ جاري التحديث وإعادة التشغيل، يرجى الانتظار... 🔨**")
    
    if HEROKU_API_KEY and HEROKU_APP_NAME:
        await deploy(event, repo, ups_rem, UPSTREAM_REPO_BRANCH)
    else:
        # نظام التحديث للاستضافات و VPS
        import shutil
        import os
        
        # 🛡️ حركة الحماية: أخذ نسخة احتياطية من الكونفك قبل التحديث
        config_path = "config.py"
        backup_path = "config_backup.temp"
        if os.path.exists(config_path):
            shutil.copy(config_path, backup_path)
            
        try:
            ups_rem.pull(UPSTREAM_REPO_BRANCH)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
            await event.edit("**⚠️ تم تصفير التغييرات المحلية لتخطي التعارض...**")
            
        # 🛡️ إرجاع الكونفك الأصلي مالتك بعد التحديث (غصباً عن الكيت هاب)
        if os.path.exists(backup_path):
            shutil.move(backup_path, config_path)

        try:
            await update_requirements()
            
            
            # 🔥 نظام خزن الآيدي حتى يجاوبك بعد ما يشتغل
            try:
                from ..sql_helper.global_collection import add_item_collectionlist
                from ..sql_helper.globals import addgvar
                add_item_collectionlist(Config.OWNER_ID, "restart_update", [event.chat_id, event.id])
                addgvar(Config.OWNER_ID, "restartupdate", "true")
            except Exception as e:
                LOGS.error(f"Error saving update state: {e}")
                
            # 📢 2. إرسال إشعار لكل الحسابات المنصبة (الحسابات الفرعية)
            try:
                from ..sql_helper.global_collectionjson import get_collections
                from telethon import TelegramClient
                from telethon.sessions import StringSession
                sub_sessions = get_collections(Config.OWNER_ID)
                if sub_sessions:
                    for sess in sub_sessions:
                        try:
                            data = sess.json
                            temp_client = TelegramClient(StringSession(data.get("session")), Config.APP_ID, Config.API_HASH)
                            await temp_client.connect()
                            await temp_client.send_message("me", "**᯽︙ تم تحديث سورس لوكجوري من قبل المالك الأساسي إلى أحدث إصدار ✓**")
                            await temp_client.disconnect()
                        except Exception:
                            pass
            except Exception as e:
                LOGS.error(f"Error notifying sub-accounts: {e}")
            
            # 🔥 رسالة التحديث مدمجة ويه التغييرات
            await event.edit(f"**✅ تم تحديث سورس لوكجوري بنجاح!**\n\n**📝 التغييرات اللي صارت:**\n{changelog}\n\n**♻️ جاري إعادة التشغيل...**")
            os.execl(sys.executable, sys.executable, "-m", "LuxuryUB")
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
            await event.edit("**⚠️ تم تصفير التغييرات المحلية والتحديث بنجاح. أعد تشغيل البوت.**")

# --- أوامر المطورين ---

@luxur.on(events.NewMessage(incoming=True))
async def dev_updates(event):
    if event.sender_id not in progs:
        return

    text = event.message.message
    if text == "تحديث اجباري" or (event.reply_to and text == "حدث"):
        await event.reply("**᯽︙ تم استلام أمر تحديث من المطور، جاري التنفيذ...**")
        event.pattern_match = type('obj', (object,), {'group': lambda i: "الان"})
        await upstream(event)