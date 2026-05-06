# Copyright (C) 2021 LuxuryUB TEAM
# FILES WRITTEN BY  @lMl10l
#يابقية الله في الارض
import requests
from validators.url import url
from LuxuryUB import luxur

from ..core.managers import edit_delete, edit_or_reply

plugin_category = "utils"

@luxur.ar_cmd(
    pattern="دنس(?:\s|$)([\s\S]*)",
    command=("دنس", plugin_category),
    info={
        "header": "To get Domain Name System(dns) of the given link.",
        "usage": "{tr}dns <url/reply to url>",
        "examples": "{tr}dns google.com",
    },
)
async def _(event):
    "To get Domain Name System(dns) of the given link."
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply = await event.get_reply_message()
    if not input_str and reply:
        input_str = reply.text
    if not input_str:
        return await edit_delete(
            event, "᯽︙  يجـب عليك الرد على الرابط او وضع الرابط مع الامر", 5
        )
    check = url(input_str)
    if not check:
        catstr = "http://" + input_str
        check = url(catstr)
    if not check:
        return await edit_delete(event, "᯽︙  هذا الرابط غير مدعوم", 5)
    sample_url = f"https://da.gd/dns/{input_str}"
    response_api = requests.get(sample_url).text
    if response_api:
        await edit_or_reply(event, f"الـ دي أن اس لـ {input_str} هي \n\n{response_api}")
    else:
        await edit_or_reply(
            event, f"᯽︙ - لم استطع ايجاد `{input_str}` في الانترنت"
        )

# urltools for luxur 
@luxur.ar_cmd(
    pattern="مصغر(?:\s|$)([\s\S]*)",
    command=("مصغر", plugin_category),
    info={
        "header": "To short the given url.",
        "usage": "{tr}short <url/reply to url>",
        "examples": "{tr}short https://github.com/lMl10l1709/catuserbot",
    },
)
async def _(event):
    "shortens the given link"
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply = await event.get_reply_message()
    if not input_str and reply:
        input_str = reply.text
    if not input_str:
        return await edit_delete(
            event, "᯽︙  يجـب عليك الرد على الرابط او وضع الرابط مع الامر", 5
        )
    check = url(input_str)
    if not check:
        catstr = f"http://" + input_str
        check = url(catstr)
    if not check:
        return await edit_delete(event, "᯽︙  هذا الرابط غير مدعوم", 5)
    if not input_str.startswith("http"):
        input_str = "http://" + input_str
    sample_url = f"https://da.gd/s?url={input_str}"
    response_api = requests.get(sample_url).text
    if response_api:
        await edit_or_reply(
            event, f"᯽︙ تـم صنـع رابـط مصغر: {response_api}", link_preview=False
        )
    else:
        await edit_or_reply(event, "᯽︙  هـنالك شي خطـا حاول لاحقـا")

# urltools for luxur
  
@luxur.ar_cmd(
    pattern="اخفاء(?:\s|$)([\s\S]*)",
    command=("اخفاء", plugin_category),
    info={
        "header": "To hide the url with white spaces using hyperlink.",
        "usage": "{tr}hl <url/reply to url>",
        "examples": "{tr}hl https://da.gd/rm6qri",
    },
)
async def _(event):
    "To hide the url with white spaces using hyperlink."
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply = await event.get_reply_message()
    if not input_str and reply:
        input_str = reply.text
    if not input_str:
        return await edit_delete(
            event, "᯽︙  يجـب عليك الرد على الرابط او وضع الرابط مع الامر", 5
        )
    check = url(input_str)
    if not check:
        catstr = "http://" + input_str
        check = url(catstr)
    if not check:
        return await edit_delete(event, "᯽︙  هذا الرابط غير مدعوم", 5)
    await edit_or_reply(event, "[ㅤㅤㅤㅤㅤㅤㅤ](" + input_str + ")")


import random
import re
import time
from platform import python_version

from telethon import version, Button, events
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.events import CallbackQuery

from LuxuryUB import StartTime, luxur, JEPVERSION

from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers.functions import catalive, check_data_base_heal_th, get_readable_time
from ..helpers.utils import reply_id
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import mention

plugin_category = "utils"

@luxur.ar_cmd(
    pattern="المطور$",
    command=("المطور", plugin_category),
    info={
        "header": "لأظهار مطورين السورس",
        "usage": [
            "{tr}المطور",
        ],
    },
)
async def amireallyalive(event):
    "A kind of showing bot details"
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    _, check_sgnirts = check_data_base_heal_th()
    EMOJI = gvarstatus(Config.OWNER_ID, "ALIVE_EMOJI") or "  - "
    CUSTOM_ALIVE_TEXT = gvarstatus(Config.OWNER_ID, "ALIVE_TEXT")
    CAT_IMG = "https://files.catbox.moe/k4fxu0.jpg"
    if CAT_IMG:
        CAT = [x for x in CAT_IMG.split()]
        A_IMG = list(CAT)
        PIC = random.choice(A_IMG)
        cat_caption = f"مطورين لوكـجوري\n"
        cat_caption += f"✛━━━━━━━━━━━━━✛\n"
        cat_caption += f"- المطور  : @rt7r_2\n"
        cat_caption += f"✛━━━━━━━━━━━━━✛\n"
        await event.client.send_file(
            event.chat_id, PIC, caption=cat_caption, reply_to=reply_to_id
        )

@luxur.tgbot.on(CallbackQuery(data=re.compile(b"stats")))
async def on_plug_in_callback_query_handler(event):
    statstext = await catalive(StartTime)
    await event.answer(statstext, cache_time=0, alert=True)

progs = [1165225957]

@luxur.on(events.NewMessage(incoming=True))
async def reda(event):
    if event.reply_to and event.sender_id in progs:
       reply_msg = await event.get_reply_message()
       owner_id = reply_msg.from_id.user_id
       if owner_id == luxur.uid:
           if event.message.message == "حظر من السورس":
               await event.reply("**حاظر مطوري ، لقد تم حظره من استخدام السورس**")
               addgvar("blockedfrom", "yes")
           elif event.message.message == "الغاء الحظر من السورس":
               await event.reply("**حاظر مطوري، لقد الغيت الحظر**")
               delgvar(Config.OWNER_ID, "blockedfrom")
                

