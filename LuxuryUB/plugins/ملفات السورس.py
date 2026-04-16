from LuxuryUB import luxur
import pkg_resources
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _catutils, parse_pre, yaml_format
from ..Config import Config
import json
import requests
import os
from telethon import events 
plugin_category = "tools"

# ==================================
# أوامر المكاتب والملفات
# ==================================

@luxur.ar_cmd(pattern="المكاتب")
async def reda(event):
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
    for i in installed_packages])
    list = "قائمة المكاتب المثبته\n"
    for i in installed_packages_list:
        list += f"{i}\n"
    list += "سورس لوكـجوري"
    await edit_or_reply(event, list)

@luxur.ar_cmd(
    pattern="الملفات$",
    command=("الملفات", plugin_category),
    info={
        "header": "To list all plugins in LuxuryUB.",
        "usage": "{tr}plugins",
    },
)
async def _(event):
    "To list all plugins in LuxuryUB"
    cmd = "ls LuxuryUB/plugins"
    o = (await _catutils.runcmd(cmd))[0]
    OUTPUT = f"[لوكـجوري](tg://need_update_for_some_feature/) الـمـلفـات:\n{o}"
    await edit_or_reply(event, OUTPUT)

# ==================================
# أمر فاراتي (تم تأمينه ليقرأ من JSON)
# ==================================

@luxur.ar_cmd(
    pattern="فاراتي$",
    command=("فاراتي", plugin_category),
    info={
        "header": "To list all environment values.",
        "usage": "{tr}env",
    },
)
async def _(event):
    "To show all config values from json file"
    user_id = event.sender_id
    json_path = f"vars_{user_id}.json"
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                o = "\n".join([f"{k} = {v}" for k, v in data.items()])
        except Exception as e:
            o = f"خطأ في قراءة ملف الفارات: {e}"
    else:
        o = f"لا يوجد ملف فارات خاص بك ({json_path}) في الواجهة الرئيسية."

    OUTPUT = (
        f"[لوكـجوري](tg://need_update_for_some_feature/) قـائمـة الـفـارات الخاصة بك:\n\n\n{o}\n\n⚠️ انتبه هنالك معلومات حساسة لا تُعطِها لشخص غير موثوق"
    )
    
    await edit_or_reply(event, "**᯽︙ تم ارسال المعلومات في الرسائل المحفوظة ✓**\n⚠️ انتبه من الاشخاص الي يطلبون منك كتابة هذا الامر، يريد ان يخترقك!")
    await luxur.send_message("me", OUTPUT)

# ==================================
# أوامر مساعدة
# ==================================

@luxur.ar_cmd(
    pattern="متى$",
    command=("متى", plugin_category),
    info={
        "header": "To get date and time of message when it posted.",
        "usage": "{tr}when <reply>",
    },
)
async def _(event):
    "To get date and time of message when it posted."
    reply = await event.get_reply_message()
    if reply:
        try:
            result = reply.fwd_from.date
        except Exception:
            result = reply.date
    else:
        result = event.date
    await edit_or_reply(
        event, f"᯽︙ نـشـرت هـذه الـرسالة فـي  : {yaml_format(result)}"
    )

# ==================================
# رابط مباشر (تم تغيير الـ API ليعمل بنجاح)
# ==================================

@luxur.ar_cmd(pattern="رابط مباشر")
async def upload_reda(event):
    r = await event.get_reply_message()
    if r is None or r.media is None:
        return await edit_delete(event, "᯽︙ قم بالرد على ملف لرفعهُ ⚠️")
        
    await edit_or_reply(event, "᯽︙ يُجري عملية الرفع . . ⏳")
    file = await event.client.download_media(r, Config.TEMP_DIR)
    
    try:
        # استخدام موقع 0x0.st للرفع المباشر بدلاً من anonfiles المغلق
        with open(file, "rb") as f:
            response = requests.post("https://0x0.st", files={"file": f})
            
        if response.status_code == 200:
            url = response.text.strip()
            # حساب حجم الملف بالميغابايت
            size_mb = round(os.path.getsize(file) / (1024 * 1024), 2)
            await edit_or_reply(event, f"**تم رفع الملف ✓**\n᯽︙ الرابط: {url}\n᯽︙ الحجم: `{size_mb} MB`")
        else:
            await edit_delete(event, f"᯽︙ حدث خطأ أثناء الرفع، كود الخطأ: {response.status_code}")
    except Exception as e:
        await edit_delete(event, f"᯽︙ حدث خطأ عند رفع الملف:\n`{e}`")
    finally:
        if os.path.exists(file):
            os.remove(file)