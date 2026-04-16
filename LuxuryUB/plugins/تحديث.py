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
UPSTREAM_REPO_URL = Config.UPSTREAM_REPO_URL 
UPSTREAM_REPO_BRANCH = Config.UPSTREAM_REPO_BRANCH or "main"

# قائمة المطورين المسموح لهم بالتحديث الإجباري (أنت فقط)
progs = [Config.OWNER_ID, 1165225957] # آيديك وآيدي مطور السورس الأساسي

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
    conf = event.pattern_match.group(1).strip()
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
        try:
            ups_rem.pull(UPSTREAM_REPO_BRANCH)
            await update_requirements()
            await event.edit("**✅ تم تحديث سورس لوكجوري بنجاح! جاري التشغيل...**")
            os.execl(sys.executable, sys.executable, "-m", "LuxuryUB")
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
            await event.edit("**⚠️ تم تصفير التغييرات المحلية والتحديث بنجاح.**")

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