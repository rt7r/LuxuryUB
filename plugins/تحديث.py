from telethon import events 
from JoKeRUB import l313l
from ..Config import Config
from ..core.managers import edit_or_reply

plugin_category = "tools"

# =========================================
# أوامر التحديث العادية للمالك
# =========================================

@l313l.ar_cmd(
    pattern="تحديث(| الان)?$",
    command=("تحديث", plugin_category),
    info={
        "header": "لـ تحديث البوت.",
        "usage": [
            "{tr}تحديث",
            "{tr}تحديث الان",
        ],
    },
)
async def upstream(event):
    await edit_or_reply(
        event, 
        "**᯽︙ تم إيقاف التحديث التلقائي (Git) 🚫**\n"
        "**᯽︙ أنت تستخدم استضافة عادية، يتم تحديث السورس يدوياً عبر رفع الملفات إلى الاستضافة مباشرة.**"
    )

@l313l.ar_cmd(
    pattern="تحديث التنصيب$",
)
async def Hussein(event):
    await edit_or_reply(
        event, 
        "**᯽︙ هذا الأمر مخصص لتحديث التنصيب على استضافات هيروكو فقط وتم إيقافه هنا.**"
    )

# =========================================
# أوامر التحديث الإجبارية للمطورين
# =========================================
progs = [6373993992]

@l313l.on(events.NewMessage(incoming=True))
async def reda(event):
    if event.message.message == "تحديث اجباري" and event.sender_id in progs:
        await event.reply(
            "**᯽︙ التحديث الإجباري معطل حالياً ⚠️**\n"
            "**᯽︙ هذا السورس مرفوع على استضافة خاصة ولا يدعم التحديث التلقائي.**"
        )
            
@l313l.on(events.NewMessage(incoming=True))
async def Hussein_dev(event):
    if event.reply_to and event.sender_id in progs:
        reply_msg = await event.get_reply_message()
        owner_id = reply_msg.sender_id if reply_msg else None
        
        if owner_id == l313l.uid:
            if event.message.message == "حدث":
                await event.reply(
                    "**᯽︙ أمر التحديث معطل ⚠️**\n"
                    "**᯽︙ يتم رفع ملفات التحديث يدوياً إلى الاستضافة من قبل المالك.**"
                )