#ترجمه فريق الجوكر على التيلكرام
from LuxuryUB import CMD_HELP, luxur

from ..core.managers import edit_delete, edit_or_reply

plugin_category = "extra"

name = "Profile Photos"


@luxur.ar_cmd(
    pattern="صورة(?: |$)(.*)",
    command=("صورة", plugin_category),
    info={
        "header": "To get user or group profile pic.",
        "description": "Reply to a user to get his profile pic or use command along\
        with profile pic number to get desired pic else use .poto all to get\
        all pics. If you don't reply to any one\
        then the bot will get the chat profile pic.",
        "usage": [
            "{tr}poto <number>",
            "{tr}poto all",
            "{tr}poto",
        ],
    },
)
async def potocmd(event):
    "To get user or group profile pic"
    uid = "".join(event.raw_text.split(maxsplit=1)[1:])
    user = await event.get_reply_message()
    chat = event.input_chat
    if user:
        photos = await event.client.get_profile_photos(user.sender)
        u = True
    else:
        photos = await event.client.get_profile_photos(chat)
        u = False
    if uid.strip() == "":
        uid = 1
        if int(uid) > (len(photos)):
            return await edit_delete(
                event, "**لم يتـم العثـور على صـورة لـهذا الـشخص ❕**"
            )
        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    elif uid.strip() == "كلها":
        if len(photos) > 0:
            await event.client.send_file(event.chat_id, photos)
        else:
            try:
                if u:  #ترجمه فريق الجوكر على التيلكرام
                    photo = await event.client.download_profile_photo(user.sender)
                else:
                    photo = await event.client.download_profile_photo(event.input_chat)
                await event.client.send_file(event.chat_id, photo)
            except Exception:
                return await edit_delete(event, "** هذا المـستخدم ليس لـديه صـورة لـعرضها 🧸♥**")
    else:
        try:
            uid = int(uid)
            if uid <= 0:
                await edit_or_reply(
                    event, "الـرقم خـطأ لا يمكن بحث أو تحميل هذه الصورة للشخص !"
                )
                return
        except BaseException:
            await edit_or_reply(event, "`لا يمكن بحث أو تحميل فقط صوره الشخص !`")
            return
        if int(uid) > (len(photos)):
            return await edit_delere(
                event, "**لم يتـم العثـور على صـورة لـهذا الـشخص ❕**"
            )

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    await event.delete()
CMD_HELP.update(
    {
        "الصورة": "**╮•❐ الامر ⦂** `.صورة` <عدد الصور (اختياري)> <بالرد على الشخص>\nالوظيفة ⦂ لأخذ صورة حساب شخص معين بالرد عليه بالامر"
    }
)
