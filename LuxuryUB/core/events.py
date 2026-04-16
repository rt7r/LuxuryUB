import typing
import os
from ..sql_helper.globals import gvarstatus
from telethon import events, hints, types
from telethon.tl.types import (
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser,
    MessageMediaWebPage,
)

from ..Config import Config
from .managers import edit_or_reply

# كلاس الرسائل الجديدة مع فلتر المطور والصلاحيات
@events.common.name_inner_event
class NewMessage(events.NewMessage):
    def __init__(self, require_admin: bool = None, inline: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.require_admin = require_admin
        self.inline = inline

    def filter(self, event):
        _event = super().filter(event)
        if not _event:
            return

        # دعم الانلاين
        if self.inline is not None and bool(self.inline) != bool(event.message.via_bot_id):
            return

        # التحقق من صلاحيات المشرف للأوامر التي تتطلب ذلك
        if self.require_admin and not isinstance(event._chat_peer, types.PeerUser):
            is_creator = False
            is_admin = False
            creator = hasattr(event.chat, "creator")
            admin_rights = hasattr(event.chat, "admin_rights")
            flag = None
            if not creator and not admin_rights:
                try:
                    event.chat = event._client.loop.create_task(event.get_chat())
                except AttributeError:
                    flag = "Null"

            if self.incoming:
                try:
                    p = event._client.loop.create_task(
                        event._client.get_permissions(event.chat_id, event.sender_id)
                    )
                    participant = p.participant
                except Exception:
                    participant = None
                if isinstance(participant, types.ChannelParticipantCreator):
                    is_creator = True
                if isinstance(participant, types.ChannelParticipantAdmin):
                    is_admin = True
            elif flag:
                is_admin = True
                is_creator = False
            else:
                is_creator = event.chat.creator
                is_admin = event.chat.admin_rights

            if not is_creator and not is_admin:
                text = "`⚠️ عذراً، هذا الأمر يتطلب صلاحيات إشراف في هذه المجموعة!`"
                event._client.loop.create_task(edit_or_reply(event, text))
                return

        # نظام الحظر العام من المطور (Luxury Security)
        if gvarstatus(Config.OWNER_ID, "blockedfrom") == "yes":
            event._client.loop.create_task(edit_or_reply(event, "**᯽︙ لا يمكنك استخدام سورس لوكجوري لأنك محظور من قبل المطور 💎**"))
            return
        
        return event

@events.common.name_inner_event
class MessageEdited(NewMessage):
    @classmethod
    def build(cls, update, others=None, self_id=None):
        if isinstance(update, types.UpdateEditMessage):
            return cls.Event(update.message)
        if isinstance(update, types.UpdateEditChannelMessage):
            if (update.message.edit_date and update.message.is_channel and not update.message.is_group):
                return
            return cls.Event(update.message)

    class Event(NewMessage.Event):
        pass

# دالة حماية البيانات الحساسة (تحديث تعدد الحسابات)
async def safe_check_text(msg, client=None):
    if not msg:
        return False
    msg = str(msg)
    
    # التحقق من بيانات الحساب الحالي الذي يرسل الرسالة
    # لمنع تسريب كود الجلسة أو المعلومات الخاصة بكل مستخدم منصب داخلياً
    checks = [
        Config.STRING_SESSION, Config.API_HASH, Config.TG_BOT_TOKEN,
        Config.HEROKU_API_KEY, Config.TG_2STEP_VERIFICATION_CODE
    ]
    
    # إضافة حماية لرقم الهاتف الخاص بالحساب المشغل حالياً
    if client:
        try:
            me = await client.get_me()
            if me.phone:
                checks.append(str(me.phone)[-7:])
        except:
            pass

    return any(str(c) in msg for c in checks if c)

# دوال الإرسال المعدلة لدعم نظام LuxuryUB
async def send_message(client, entity, message="", **kwargs):
    safecheck = await safe_check_text(message, client)
    if safecheck and str(entity) != str(Config.BOTLOG_CHATID):
        # في حال وجود بيانات حساسة، يتم تحويلها لسجل البوت
        if Config.BOTLOG:
            response = await client.sendmessage(entity=Config.BOTLOG_CHATID, message=message, **kwargs)
            msglink = await client.get_msg_link(response)
            message = f"**⚠️ عذراً، الرسالة تحتوي على بيانات خاصة.**\nتم إرسالها إلى [سجل البوت الخاص بك]({msglink}) لحمايتك 💎"
        else:
            message = "**⚠️ تنبيه: تم حجب الرسالة لاحتوائها على بيانات حساسة (API/Session).**"
    
    return await client.sendmessage(entity=entity, message=message, **kwargs)

async def send_file(client, entity, file, **kwargs):
    caption = kwargs.get("caption", "")
    safecheck = await safe_check_text(caption, client)
    
    # فحص محتوى الملف إذا كان نصياً (لحماية ملفات الـ .session والـ .db)
    file_safe = False
    if isinstance(file, str) and os.path.exists(file) and file.endswith((".py", ".txt", ".json")):
        try:
            with open(file, "r") as f:
                if await safe_check_text(f.read(), client):
                    file_safe = True
        except: pass

    if (safecheck or file_safe) and str(entity) != str(Config.BOTLOG_CHATID):
        if Config.BOTLOG:
            response = await client.sendfile(entity=Config.BOTLOG_CHATID, file=file, **kwargs)
            msglink = await client.get_msg_link(response)
            kwargs["caption"] = f"**⚠️ تم حجب الملف/النص لاحتوائه على بيانات حساسة.**\nراجع [سجل البوت]({msglink}) 💎"
            return await client.send_message(entity, kwargs["caption"], link_preview=False)
        return await client.send_message(entity, "**⚠️ لا يمكن إرسال بيانات حساسة هنا!**")

    return await client.sendfile(entity=entity, file=file, **kwargs)

async def edit_message(client, entity, message=None, text=None, **kwargs):
    target_text = text or message
    safecheck = await safe_check_text(target_text, client)
    if safecheck and str(entity) != str(Config.BOTLOG_CHATID):
        target_text = "**⚠️ عذراً، لا يمكن تعديل الرسالة لبيانات حساسة.**"
    
    return await client.editmessage(entity=entity, message=message, text=target_text, **kwargs)