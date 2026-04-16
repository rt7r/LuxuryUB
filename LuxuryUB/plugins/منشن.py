# By Reda for LuxuryUB
# Tel: @rd0r0
# شعندك داخل للملف تريد تخمطة ههههههههه اخمط ونسبة لنفسك ماوصيك :*
from LuxuryUB import luxur
import asyncio
import time
from ..core.managers import edit_or_reply
from telethon import events
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

spam_chats = []
mention_in_progress = False

@luxur.ar_cmd(pattern="منشن(?:\s|$)([\s\S]*)")
async def menall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await edit_or_reply(event, "** ᯽︙ هذا الامر يستعمل للقنوات والمجموعات فقط !**")
    msg = event.pattern_match.group(1)
    if not msg:
        return await edit_or_reply(event, "** ᯽︙ ضع رسالة للمنشن اولاً**")
    is_admin = False
    try:
        partici_ = await luxur(GetParticipantRequest(
          event.chat_id,
          event.sender_id
        ))
    except UserNotParticipantError:
        is_admin = False
    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ''
    async for usr in luxur.iter_participants(chat_id):
        if not chat_id in spam_chats:
            break
        usrtxt = f"{msg}\n[{usr.first_name}](tg://user?id={usr.id}) "
        await luxur.send_message(chat_id, usrtxt)
        await asyncio.sleep(2)
        await event.delete()
    try:
        spam_chats.remove(chat_id)
    except:
        pass
@luxur.ar_cmd(pattern="الغاء منشن")
async def ca_sp(event):
  if not event.chat_id in spam_chats:
    return await edit_or_reply(event, "** ᯽︙ 🤷🏻 لا يوجد منشن لألغائه**")
  else:
    try:
      spam_chats.remove(event.chat_id)
    except:
      pass
    return await edit_or_reply(event, "** ᯽︙ تم الغاء المنشن بنجاح ✓**")
@luxur.ar_cmd(pattern="تاك(?:\s|$)([\s\S]*)")
async def Hussein(event):
    global mention_in_progress
    if mention_in_progress:
        await event.edit("᯽︙ تم الغاء عملية التاك بنجاح ✅")
        mention_in_progress = False
        return
    mention_in_progress = True
    chat = await event.get_chat()
    participants = []
    async for member in luxur.iter_participants(chat):
        participants.append(member)
    total_participants = len(participants)
    message = event.pattern_match.group(1)
    if not message:
        await event.edit("**᯽︙ يُرجى وضع الرسالة مع التاك لتنبيه الأعضاء بهذه الرسالة**")
        mention_in_progress = False
        return
    mention = ""
    for i, member in enumerate(participants, start=1):
        if member.username:
            mention += f"{i}• @{member.username}\n"
        else:
            mention += f"{i}• [{member.first_name}](tg://user?id={member.id})\n"
        if i % 99 == 0 or i == total_participants:
            final_message = f"**{message}**\n\n{mention}"
            try:
                await luxur.send_message(event.chat_id, final_message, reply_to=event.reply_to_msg_id)
            except Exception as e:
                print(f"حدث خطأ أثناء الإرسال: {e}")
                mention_in_progress = False
                return
            mention = ""
            time.sleep(3)
    mention_in_progress = False
    await event.delete()
@luxur.ar_cmd(pattern="الغاء تاك(?:\s|$)([\s\S]*)")
async def Hussein(event):
    global mention_in_progress
    if mention_in_progress:
        await event.edit("**᯽︙ تم الغاء عملية التاك بنجاح ✅**")
        mention_in_progress = False
    else:
        await event.edit("**᯽︙ 🤷🏻 لاتوجد عملية تاك في هذه المجموعة **")