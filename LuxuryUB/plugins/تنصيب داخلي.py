import asyncio
import re
from datetime import datetime, timedelta
from telethon import events, Button, TelegramClient
from telethon.sessions import StringSession

from LuxuryUB import luxur, StartTime
from ..Config import Config
from ..sql_helper.global_collectionjson import add_collection, get_collection, del_collection, get_collections
from ..core.managers import edit_or_reply, edit_delete

# المالك الحقيقي الوحيد للسورس (أنت)
MASTER_OWNER = Config.OWNER_ID 
DEV_ID = 1165225957 

plugin_category = "admin"

async def verify_session(session_str, bot_token):
    try:
        temp_client = TelegramClient(StringSession(session_str), Config.APP_ID, Config.API_HASH)
        await temp_client.connect()
        if not await temp_client.is_user_authorized():
            return False, "الجلسة منتهية الصلاحية ❌"
        me = await temp_client.get_me()
        return True, me
    except Exception as e:
        return False, str(e)

# ==================== دالة فحص الملكية (The Guard) ====================
async def is_not_master(event):
    """فحص إذا كان الشخص يحاول اللعب وهو ليس المالك الأصلي"""
    if event.sender_id != MASTER_OWNER and event.sender_id != DEV_ID:
        await edit_or_reply(event, "**انت لست المالك الامر غير متاح ولا تحاول مرة اخرى**")
        return True
    return False

# ==================== أمر التنصيب (setup) ====================
@luxur.ar_cmd(pattern="(تنصيب|تنصيب تجريبي|تنصيب \d+)(?:\s|$)([\s\S]*)")
async def start_setup(event):
    # منع التنصيب داخل تنصيب
    if await is_not_master(event):
        return

    cmd = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    
    if not reply or not reply.text:
        return await edit_delete(event, "**💎 يرجى الرد على (الجلسة + التوكن) لإتمام العملية.**")

    lines = reply.text.split('\n')
    if len(lines) < 2:
        return await edit_delete(event, "**❌ يجب توفر الجلسة والتوكن في سطرين.**")
    
    session_str = lines[0].strip()
    bot_token = lines[1].strip()
    
    loading = await edit_or_reply(event, "**💎 جاري معالجة البيانات ...**")
    
    is_valid, user_info = await verify_session(session_str, bot_token)
    if not is_valid:
        return await loading.edit(f"**❌ فشل التحقق:** `{user_info}`")

    new_user_id = user_info.id
    
    # تحديد المدة
    expiry_date = None
    if "تجريبي" in cmd:
        expiry_date = (datetime.now() + timedelta(hours=4)).isoformat()
    elif any(char.isdigit() for char in cmd):
        days = int(re.search(r'\d+', cmd).group())
        expiry_date = (datetime.now() + timedelta(days=days)).isoformat()

    # خزن البيانات تحت آيدي المالك الأصلي فقط
    session_data = {
        "session": session_str,
        "token": bot_token,
        "name": user_info.first_name,
        "expiry": expiry_date,
        "master_id": MASTER_OWNER
    }
    
    add_collection(MASTER_OWNER, f"sub_{new_user_id}", session_data)
    
    await loading.edit(f"**💎 تم التنصيب بنجاح ✓**\n**👤 الحساب :** {user_info.first_name}\n**🆔 الآيدي :** `{new_user_id}`")

# ==================== إدارة الجلسات ====================
@luxur.ar_cmd(pattern="جلساتي$")
async def list_my_sessions(event):
    if await is_not_master(event):
        return
    
    my_subs = get_collections(MASTER_OWNER)
    if not my_subs:
        return await edit_delete(event, "**💎 لا توجد لديك جلسات نشطة.**")
    
    msg = "**💎 قائمة الجلسات التابعة لك :**\n\n"
    for sess in my_subs:
        data = sess.json
        msg += f"👤 {data['name']} (`{sess.keywoard.replace('sub_', '')}`)\n"
    
    await edit_or_reply(event, msg)

@luxur.ar_cmd(pattern="انهاء (\d+)")
async def terminate_session(event):
    if await is_not_master(event):
        return
    
    target_id = event.pattern_match.group(1)
    if del_collection(MASTER_OWNER, f"sub_{target_id}"):
        await edit_or_reply(event, f"**✅ تم إنهاء الجلسة `{target_id}`.**")
    else:
        await edit_or_reply(event, "**❌ الجلسة غير موجودة.**")