import random
import re
import json
import os
import time
from datetime import datetime

from telethon import Button, functions
from telethon.events import CallbackQuery
from telethon.utils import get_display_name

from LuxuryUB import luxur
from LuxuryUB.core.logger import logging

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event, reply_id
from ..sql_helper import global_collectionjson as sql
from ..sql_helper import global_list as sqllist
from ..sql_helper import pmpermit_sql
from . import mention

LOGS = logging.getLogger(__name__)
cmdhd = Config.COMMAND_HAND_LER

# =======================================================
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
# =======================================================

RECENT_REPLIES = {}

async def do_pm_permit_action(event, chat):
    reply_to_id = await reply_id(event)
    client_id = event.client.uid
    db = get_db(client_id)
    pm_mode = db.get("pmpermit_mode", "protect") 

    me = await event.client.get_me()
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    first = chat.first_name
    last = chat.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{chat.username}" if chat.username else mention
    userid = chat.id
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention

    # =========================================================
    if pm_mode == "reply_only":
        current_time = time.time()
        last_reply = RECENT_REPLIES.get(str(chat.id), 0)
        
        # إذا لم تمر 10 دقائق (600 ثانية)، تجاهل ولا ترد
        if current_time - last_reply < 600:
            return
            
        # تحديث وقت آخر رد لهذا الشخص
        RECENT_REPLIES[str(chat.id)] = current_time
        
        custompmpermit = db.get("pmpermit_txt")
        if custompmpermit:
            USER_BOT_NO_WARN = custompmpermit.format(
                mention=mention, first=first, last=last, fullname=fullname, username=username,
                userid=userid, my_first=my_first, my_last=my_last, my_fullname=my_fullname,
                my_username=my_username, my_mention=my_mention, totalwarns="∞",
                warns=0, remwarns="∞",
            )
        else:
            USER_BOT_NO_WARN = f"᯽︙ اهلا بك {mention} \n مالك الحساب غير موجود حاليا، اترك رسالتك وسيرد عليك لاحقاً 🌿."

        try:
            PM_PIC = db.get("pmpermit_pic")
            if PM_PIC:
                CAT = [x for x in PM_PIC.split()]
                PIC = list(CAT)
                CAT_IMG = random.choice(PIC)
                await event.client.send_file(
                    chat.id, CAT_IMG, caption=USER_BOT_NO_WARN, reply_to=reply_to_id, force_document=False,
                )
            else:
                await event.client.send_message(chat.id, USER_BOT_NO_WARN, reply_to=reply_to_id)
        except Exception as e:
            LOGS.error(e)
            await event.reply(USER_BOT_NO_WARN)
            
        return 

    # =========================================================
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}
    try: PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError: PMMESSAGE_CACHE = {}
    
    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0
        
    try: MAX_FLOOD_IN_PMS = int(db.get("MAX_FLOOD_IN_PMS") or 6)
    except (ValueError, TypeError): MAX_FLOOD_IN_PMS = 6
    
    totalwarns = MAX_FLOOD_IN_PMS + 1
    warns = PM_WARNS[str(chat.id)] + 1
    remwarns = totalwarns - warns

    if PM_WARNS[str(chat.id)] >= MAX_FLOOD_IN_PMS:
        try:
            if str(chat.id) in PMMESSAGE_CACHE:
                await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                del PMMESSAGE_CACHE[str(chat.id)]
        except Exception as e:
            LOGS.info(str(e))
            
        custompmblock = db.get("pmblock")
        if custompmblock:
            USER_BOT_WARN_ZERO = custompmblock.format(
                mention=mention, first=first, last=last, fullname=fullname, username=username,
                userid=userid, my_first=my_first, my_last=my_last, my_fullname=my_fullname,
                my_username=my_username, my_mention=my_mention, totalwarns=totalwarns,
                warns=warns, remwarns=remwarns,
            )
        else:
            USER_BOT_WARN_ZERO = f"- حذࢪتك وكتلك لا تكࢪࢪ تَم حظࢪك بنجاح ما ٱكدر اخليك تزعج المالك \n- - بباي 🙁🤍"
            
        msg = await event.reply(USER_BOT_WARN_ZERO)
        await event.client(functions.contacts.BlockRequest(chat.id))
        
        the_message = f"#المحظورين_الحمايه\n[{get_display_name(chat)}](tg://user?id={chat.id}) تم حظره\n- عدد الرسائل: {PM_WARNS[str(chat.id)]}"
        del PM_WARNS[str(chat.id)]
        sql.del_collection("pmwarns")
        sql.del_collection("pmmessagecache")
        sql.add_collection("pmwarns", PM_WARNS, {})
        sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
        try:
            from . import BOTLOG_CHATID
            return await event.client.send_message(BOTLOG_CHATID, the_message)
        except BaseException:
            return

    custompmpermit = db.get("pmpermit_txt")
    if custompmpermit:
        USER_BOT_NO_WARN = custompmpermit.format(
            mention=mention, first=first, last=last, fullname=fullname, username=username,
            userid=userid, my_first=my_first, my_last=my_last, my_fullname=my_fullname,
            my_username=my_username, my_mention=my_mention, totalwarns=totalwarns,
            warns=warns, remwarns=remwarns,
        )
    else:
        USER_BOT_NO_WARN = f"᯽︙ اهلا بك {mention} \n مالك الحساب غير موجود حاليا الرجاء الانتظار وعدم تكرار الرسائل.\n\nلديك {warns}/{totalwarns} من التحذيرات لا تكرر الرسائل. "

    PM_WARNS[str(chat.id)] += 1

    try:
        PM_PIC = db.get("pmpermit_pic")
        if PM_PIC:
            CAT = [x for x in PM_PIC.split()]
            PIC = list(CAT)
            CAT_IMG = random.choice(PIC)
            msg = await event.client.send_file(
                chat.id, CAT_IMG, caption=USER_BOT_NO_WARN, reply_to=reply_to_id, force_document=False,
            )
        else:
            msg = await event.client.send_message(chat.id, USER_BOT_NO_WARN, reply_to=reply_to_id)
    except Exception as e:
        LOGS.error(e)
        msg = await event.reply(USER_BOT_NO_WARN)

    try:
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
    except Exception as e:
        LOGS.info(str(e))
        
    PMMESSAGE_CACHE[str(chat.id)] = msg.id
    sql.del_collection("pmwarns")
    sql.del_collection("pmmessagecache")
    sql.add_collection("pmwarns", PM_WARNS, {})
    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})


@luxur.ar_cmd(pattern="الحماية (تشغيل|تعطيل|رد)$")
async def pmpermit_on(event):
    client_id = event.client.uid
    input_str = event.pattern_match.group(1)
    db = get_db(client_id)

    if input_str == "تشغيل":
        db["pmpermit"] = "true"
        db["pmpermit_mode"] = "protect"
        save_db(client_id, db)
        await edit_delete(event, "**- تم تفعيل الحماية مع الحظر التلقائي ✅**")
        
    elif input_str == "رد":
        db["pmpermit"] = "true"
        db["pmpermit_mode"] = "reply_only"
        save_db(client_id, db)
        await edit_delete(event, "**- تم تفعيل الرد التلقائي الذكي (فاصل 10 دقائق) 🌿✅**")
        
    elif input_str == "تعطيل":
        if "pmpermit" in db:
            del db["pmpermit"]
        if "pmpermit_mode" in db:
            del db["pmpermit_mode"]
        save_db(client_id, db)
        await edit_delete(event, "**- تم تعطيل الحماية والرد التلقائي ❌**")


@luxur.ar_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def on_new_private_message(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return
        
    chat = await event.get_chat()
    if chat.bot or chat.verified:
        return
    if pmpermit_sql.is_approved(chat.id):
        return
        
        
    await do_pm_permit_action(event, chat)


@luxur.ar_cmd(outgoing=True, func=lambda e: e.is_private, edited=False, forword=None)
async def you_dm_other(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return
        
    chat = await event.get_chat()
    if chat.bot or chat.verified:
        return

    if event.text and event.text.startswith((f"{cmdhd}بلوك", f"{cmdhd}رفض", f"{cmdhd}س", f"{cmdhd}ر", f"{cmdhd}سماح")):
        return
        
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError:
        PM_WARNS = {}
        
    start_date = str(datetime.now().strftime("%B %d, %Y"))
    if not pmpermit_sql.is_approved(chat.id) and str(chat.id) not in PM_WARNS:
        pmpermit_sql.approve(chat.id, get_display_name(chat), start_date, chat.username, "لم يتم رفضه")
        try:
            PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
        except AttributeError:
            PMMESSAGE_CACHE = {}
        if str(chat.id) in PMMESSAGE_CACHE:
            try:
                await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            except Exception as e:
                LOGS.info(str(e))
            del PMMESSAGE_CACHE[str(chat.id)]
        sql.del_collection("pmmessagecache")
        sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})


@luxur.ar_cmd(pattern="(س|سماح)(?:\s|$)([\s\S]*)")
async def approve_p_m(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return await edit_delete(event, f"- يجب تفعيل امر الحماية اولا بأرسال `{cmdhd}الحماية تشغيل`")
        
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        user, reason = await get_user_from_event(event, secondgroup=True)
        if not user: return
        
    if not reason: reason = "لم يذكر"
    
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}
    
    if not pmpermit_sql.is_approved(user.id):
        if str(user.id) in PM_WARNS: del PM_WARNS[str(user.id)]
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        pmpermit_sql.approve(user.id, get_display_name(user), start_date, user.username, reason)
        
        await edit_delete(event, f"-  [{user.first_name}](tg://user?id={user.id})\n- تم السماح له بأرسال الرسائل \nالسبب : {reason}")
        
        try: PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
        except AttributeError: PMMESSAGE_CACHE = {}
        
        if str(user.id) in PMMESSAGE_CACHE:
            try: await event.client.delete_messages(user.id, PMMESSAGE_CACHE[str(user.id)])
            except Exception: pass
            del PMMESSAGE_CACHE[str(user.id)]
            
        sql.del_collection("pmwarns")
        sql.del_collection("pmmessagecache")
        sql.add_collection("pmwarns", PM_WARNS, {})
        sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
    else:
        await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id}) \n - هو بالفعل في قائمة السماح")


@luxur.ar_cmd(pattern="(ر|رفض)(?:\s|$)([\s\S]*)")
async def disapprove_p_m(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return await edit_delete(event, f"- يجب تفعيل امر الحماية اولا بأرسال `{cmdhd}الحماية تشغيل`")
        
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        reason = event.pattern_match.group(2)
        if reason != "الكل":
            user, reason = await get_user_from_event(event, secondgroup=True)
            if not user: return
            
    if reason == "الكل":
        pmpermit_sql.disapprove_all()
        return await edit_delete(event, "- حسنا تم رفض الجميع بنجاح ")
        
    if not reason: reason = "لم يذكر"
    
    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        await edit_or_reply(event, f"[{user.first_name}](tg://user?id={user.id})\n- تم رفضه من أرسال الرسائل\nالسبب: {reason}")
    else:
        await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id})\n - لم يتم الموافقة عليه بالأصل")


@luxur.ar_cmd(pattern="بلوك(?:\s|$)([\s\S]*)")
async def block_p_m(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return await edit_delete(event, f"- يجب تفعيل امر الحماية اولا بأرسال `{cmdhd}الحماية تشغيل`")
        
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
        
    if not reason: reason = "لم يتم ذكره"
    
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}
    try: PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError: PMMESSAGE_CACHE = {}
    
    if str(user.id) in PM_WARNS: del PM_WARNS[str(user.id)]
    if str(user.id) in PMMESSAGE_CACHE:
        try: await event.client.delete_messages(user.id, PMMESSAGE_CACHE[str(user.id)])
        except Exception: pass
        del PMMESSAGE_CACHE[str(user.id)]
        
    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        
    sql.del_collection("pmwarns")
    sql.del_collection("pmmessagecache")
    sql.add_collection("pmwarns", PM_WARNS, {})
    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
    
    await event.client(functions.contacts.BlockRequest(user.id))
    await edit_delete(event, f"[{user.first_name}](tg://user?id={user.id})\n تم حظره بنجاح لا يمكنه مراسلتك بعد الان \nالسبب: {reason}")


@luxur.ar_cmd(pattern="انبلوك(?:\s|$)([\s\S]*)")
async def unblock_pm(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return await edit_delete(event, f"- يجب تفعيل امر الحماية اولا بأرسال `{cmdhd}الحماية تشغيل`")
        
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
        
    if not reason: reason = "لم يتم ذكر السبب"
    await event.client(functions.contacts.UnblockRequest(user.id))
    await event.edit(f"[{user.first_name}](tg://user?id={user.id}) \nتم الغاء حظره بنجاح يمكنه التكلم معك الان \nالسبب: {reason}")


@luxur.ar_cmd(pattern="المسموح لهم$")
async def get_approved_p_m(event):
    client_id = event.client.uid
    db = get_db(client_id)
    if not db.get("pmpermit"):
        return await edit_delete(event, f"- يجب تفعيل امر الحماية اولا بأرسال `{cmdhd}الحماية تشغيل`")
        
    approved_users = pmpermit_sql.get_all_approved()
    APPROVED_PMs = "- قائمة المسموح لهم الحالية\n\n"
    if len(approved_users) > 0:
        for user in approved_users:
            APPROVED_PMs += f"• 👤 {_format.mentionuser(user.first_name , user.user_id)}\n- الأيدي: `{user.user_id}`\n- المعرف: @{user.username}\n- التاريخ: {user.date}\n- السبب: {user.reason}\n\n"
    else:
        APPROVED_PMs = "انت لم توافق على اي شخص بالاصل ️"
        
    await edit_or_reply(
        event, APPROVED_PMs, file_name="قائمة الحماية لوكـجوري.txt",
        caption="قائمة المسموح لهم الحالية\n سورس لوكـجوري \n @ee2en",
    )