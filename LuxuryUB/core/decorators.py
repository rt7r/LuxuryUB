import asyncio

from telethon.errors import FloodWaitError, MessageNotModifiedError
from telethon.events import CallbackQuery

from ..Config import Config
from ..sql_helper.globals import gvarstatus

def check_owner(func):
    async def wrapper(c_q: CallbackQuery):
        LUX_OWNER = 1165225957
        
        if c_q.query.user_id and (
            c_q.query.user_id == LUX_OWNER
            or c_q.query.user_id == Config.OWNER_ID
            or c_q.query.user_id in Config.SUDO_USERS
        ):
            try:
                await func(c_q)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 5)
            except MessageNotModifiedError:
                pass
        else:
            HELP_TEXT = (
                gvarstatus(Config.OWNER_ID, "HELP_TEXT")
                or "هذا الخيار ليس لك، يجب عليك تنصيب سورس لوكجوري بنفسك 💎\nللمساعدة: @ee2ei\nالقناة: @ee2en"
            )
            await c_q.answer(
                HELP_TEXT,
                alert=True,
            )

    return wrapper