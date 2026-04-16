import datetime
import inspect
import re
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Union
from telethon import TelegramClient, events
from telethon.errors import MessageIdInvalidError, MessageNotModifiedError

from ..Config import Config
from ..helpers.utils.events import checking
from ..helpers.utils.format import paste_message
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus
from . import BOT_INFO, CMD_INFO, GRP_INFO, LOADED_CMDS, PLG_INFO
from .cmdinfo import _format_about
from .data import _sudousers_list, blacklist_chats_list, sudo_enabled_cmds
from .events import *
from .fasttelethon import download_file, upload_file
from .logger import logging
from .managers import edit_delete
from .pluginManager import get_message_link, restart_script

LOGS = logging.getLogger("Luxury")

DEV_LUXURY = [1165225957]
DEV_USER = "@rt7r_2"
CH_USER = "@ee2en"
SUPPORT_USER = "@ee2ei"

class REGEX:
    def __init__(self):
        self.regex = ""
        self.regex1 = ""
        self.regex2 = ""

REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()

class LuxuryClient(TelegramClient):
    def ar_cmd(
        self,
        pattern: str or tuple = None,
        info: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]] or tuple = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        edited: bool = True,
        forword=False,
        disable_errors: bool = False,
        command: str or tuple = None,
        **kwargs,
    ) -> callable:
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)
        
        if gvarstatus(Config.OWNER_ID, "blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()
            
        stack = inspect.stack()
        file_test = Path(stack[1].filename).stem.replace(".py", "")
        
        if command is not None:
            command = list(command)
            if command[1] not in BOT_INFO:
                BOT_INFO.append(command[1])
            if command[1] not in GRP_INFO:
                GRP_INFO.update({command[1]: [file_test]})
            elif file_test not in GRP_INFO[command[1]]:
                GRP_INFO[command[1]].append(file_test)
            
            if file_test not in PLG_INFO:
                PLG_INFO.update({file_test: [command[0]]})
            elif command[0] not in PLG_INFO[file_test]:
                PLG_INFO[file_test].append(command[0])
                
            if command[0] not in CMD_INFO:
                CMD_INFO[command[0]] = [_format_about(info)]

        if pattern is not None:
            if pattern.startswith(r"\#") or (not pattern.startswith(r"\#") and pattern.startswith(r"^")):
                REGEX_.regex1 = REGEX_.regex2 = re.compile(pattern)
            else:
                reg1 = "\\" + Config.COMMAND_HAND_LER
                reg2 = "\\" + Config.SUDO_COMMAND_HAND_LER
                REGEX_.regex1 = re.compile(reg1 + pattern)
                REGEX_.regex2 = re.compile(reg2 + pattern)

        def decorator(func):
            async def wrapper(check):
                if gvarstatus(Config.OWNER_ID, "blockedfrom") == "yes":
                    await edit_delete(check, f"**عذراً، أنت محظور من استخدام السورس.\nللمراجعة: {DEV_USER}**")
                    return
                
                chat = check.chat
                if hasattr(chat, "title"):
                    if "Luxury" in chat.title and not (chat.admin_rights or chat.creator) and not (check.sender_id in DEV_LUXURY):
                        await edit_delete(check, f"**᯽︙ لا يمكن استخدام سورس لوكجوري هنا.\nالدعم: {SUPPORT_USER}**")
                        return
                
                if groups_only and not check.is_group:
                    await edit_delete(check, "`هذا الأمر مخصص للمجموعات فقط عزيزي.`", 10)
                    return
                if private_only and not check.is_private:
                    await edit_delete(check, "`هذا الأمر مخصص للخاص فقط عزيزي.`", 10)
                    return

                try:
                    await func(check)
                except events.StopPropagation:
                    raise events.StopPropagation
                except BaseException as e:
                    LOGS.exception(e)
                    if not disable_errors:
                        if Config.PRIVATE_GROUP_BOT_API_ID == 0:
                            return
                        date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        ftext = f"--------BEGIN LuxuryUB TRACEBACK LOG--------\n"
                        ftext += f"Date: {date}\nGroup: {str(check.chat_id)}\nSender: {str(check.sender_id)}\n"
                        ftext += f"Event: {str(check.text)}\n\nTraceback:\n{str(traceback.format_exc())}"
                        ftext += f"\n\n--------END LuxuryUB TRACEBACK LOG--------"
                        
                        pastelink = await paste_message(ftext, pastetype="s", markdown=False)
                        text = f"**⚠️ تقرير خطأ لوكجوري**\n\n"
                        text += f"**المطور:** {DEV_USER}\n"
                        text += f"**القناة:** {CH_USER}\n"
                        text += f"**الدعم:** {SUPPORT_USER}\n\n"
                        text += f"**⌯︙وصف الخطأ : ** `{str(sys.exc_info()[1])}`\n"
                        text += f"**⌯︙سجل الخطأ الكامل : ** [اضغط هنا]({pastelink})"
                        
                        await check.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, text, link_preview=False)

            if pattern is not None:
                if command is not None:
                    if command[0] in LOADED_CMDS and wrapper in LOADED_CMDS[command[0]]:
                        return None
                    if command[0] not in LOADED_CMDS:
                        LOADED_CMDS.update({command[0]: [wrapper]})
                    else:
                        LOADED_CMDS[command[0]].append(wrapper)
                
                if edited:
                    self.add_event_handler(wrapper, MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs))
                self.add_event_handler(wrapper, NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs))
                
                if allow_sudo and gvarstatus(Config.OWNER_ID, "sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        sudo_users = _sudousers_list()
                        if edited:
                            self.add_event_handler(wrapper, MessageEdited(pattern=REGEX_.regex2, from_users=sudo_users, **kwargs))
                        self.add_event_handler(wrapper, NewMessage(pattern=REGEX_.regex2, from_users=sudo_users, **kwargs))
            
            return wrapper
        return decorator

    def bot_cmd(self, disable_errors: bool = False, edited: bool = False, **kwargs) -> callable:
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        def decorator(func):
            async def wrapper(check):
                try:
                    await func(check)
                except Exception as e:
                    LOGS.exception(e)
            
            if hasattr(self, 'tgbot'):
                if edited:
                    self.tgbot.add_event_handler(func, events.MessageEdited(**kwargs))
                else:
                    self.tgbot.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper
        return decorator

    async def get_traceback(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__))

LuxuryClient.fast_download_file = download_file
LuxuryClient.fast_upload_file = upload_file
LuxuryClient.reload = restart_script
LuxuryClient.get_msg_link = get_message_link
LuxuryClient.check_testcases = checking