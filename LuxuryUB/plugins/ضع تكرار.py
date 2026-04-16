import asyncio

from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from ..sql_helper import antiflood_sql as sql
from ..utils import is_admin
from . import luxur, edit_or_reply

plugin_category = "admin"
CHAT_FLOOD = sql.__load_flood_settings()

ANTI_FLOOD_WARN_MODE = ChatBannedRights(
    until_date=None, view_messages=None, send_messages=True
)


@luxur.ar_cmd(incoming=True, groups_only=True)
async def _(event):
    if not CHAT_FLOOD:
        return
    catadmin = await is_admin(event.client, event.chat_id, event.client.uid)
    if not catadmin:
        return
    if str(event.chat_id) not in CHAT_FLOOD:
        return
    should_ban = sql.update_flood(event.chat_id, event.message.sender_id)
    if not should_ban:
        return
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id, event.message.sender_id, ANTI_FLOOD_WARN_MODE
            )
        )
    except Exception as e:
        no_admin_privilege_message = await event.client.send_message(
            entity=event.chat_id,
            message=f"""**بـوت مـانع الـتكرار**
@admin [المستخدم](tg://user?id={event.message.sender_id}) قـام بالتكرار في هذه الدردشه.
`{str(e)}`""",
            reply_to=event.message.id,
        )
        await asyncio.sleep(4)
        await no_admin_privilege_message.edit(
            "** هذا التكرار ما يفيدك اخي استمتع بالدردشة مثل الناس 🧸💞** "
        )
    else:
        await event.client.send_message(
            entity=event.chat_id,
            message=f"""**بـوت مـانع الـتكرار**
[المستخدم](tg://user?id={event.message.sender_id}) \n قـام بتجاوز عدد الـتكرار
لـذلك تـم تقيـيده""",
            reply_to=event.message.id,
        )


@luxur.ar_cmd(
    pattern="ضع تكرار(?: |$)(.*)",
    command=("ضع تكرار", plugin_category),
    info={
        "header": "To setup antiflood in a group",
        "description": "It warns the user if he spams the chat and if you are an admin with proper rights then it mutes him in that group.",
        "note": "To stop antiflood setflood with high value like 999999",
        "usage": "{tr}setflood <count>",
        "examples": [
            "{tr}setflood 10",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def _(event):
    "To setup antiflood in a group to prevent spam"
    input_str = event.pattern_match.group(1)
    event = await edit_or_reply(event, "** تم تحديث عدد التكرار 🧸♥**")
    await asyncio.sleep(2)
    try:
        sql.set_flood(event.chat_id, input_str)
        sql.__load_flood_settings()
        await event.edit(f"تم تحديث عدد الـتكرار لـ {input_str} في الدردشه الحالية")
    except Exception as e:
        await event.edit(str(e))
# For Catuserbot
# Arabic Translate By  :  @lMl10l
