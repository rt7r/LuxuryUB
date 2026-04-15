import os
import json
import asyncio
from datetime import datetime as dt
from PIL import Image, ImageDraw, ImageFont
from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz

from JoKeRUB import l313l
from ..Config import Config
from ..core.managers import edit_or_reply
from . import reply_id

plugin_category = "utils"

FONT_FILE_TO_USE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def get_user_timezone(user_id):
   
    json_path = f"vars_{user_id}.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
              
                return data.get("TZ") or data.get("timezone") or Config.TZ or "Asia/Baghdad"
        except:
            pass
    return Config.TZ or "Asia/Baghdad"

async def get_tz(con):
    for c_code, c_name in c_n.items():
        if con.lower() == c_name.lower() or con.upper() == c_code:
            return c_tz.get(c_code)
    return None

# --- أمر .توقيت ---
@l313l.ar_cmd(
    pattern="توقيت(?:\s|$)([\s\S]*)(?<![0-9])(?: |$)([0-9]+)?",
    command=("توقيت", plugin_category),
)
async def time_func(tdata):
    con = tdata.pattern_match.group(1).strip()
    tz_num = tdata.pattern_match.group(2)
    t_form = "%I:%M %p"
    d_form = "%Y/%m/%d"
    
    
    user_tz_str = get_user_timezone(tdata.sender_id)
    
    if not con:
       
        now = dt.now(tz(user_tz_str))
        return await edit_or_reply(
            tdata, 
            f"᯽︙ الـساعة الآن: `{now.strftime(t_form)}`\n᯽︙ تـاريخ اليوم: `{now.strftime(d_form)}`"
        )

    timezones = await get_tz(con)
    if not timezones:
        return await edit_or_reply(tdata, "᯽︙ البلد غير صحيح (اكتبه بالانجليزي، مثال: Iraq)")

    target_tz_str = timezones[int(tz_num)-1] if tz_num else timezones[0]
    
   
    now = dt.now(tz(target_tz_str))
    
    await edit_or_reply(
        tdata,
        f"᯽︙ الـوقت في **{con}**:\n"
        f"᯽︙ الـساعة: `{now.strftime(t_form)}`\n"
        f"᯽︙ الـتاريخ: `{now.strftime(d_form)}`"
    )
    
@l313l.ar_cmd(
    pattern="الوقت(?:\s|$)([\s\S]*)",
    command=("الوقت", plugin_category),
)
async def _(event):
    reply_msg_id = await reply_id(event)
    
    
    user_tz_str = get_user_timezone(event.sender_id)
    
    now = dt.now(tz(user_tz_str))
    time_str = now.strftime("%I:%M:%S")
    date_str = now.strftime("%d.%m.%y")
    
    current_time = (
        "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡\n"
        "⚡ JoKeRUB ⚡\n"
        "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡\n"
        f"  {os.path.basename(user_tz_str)}\n"
        f"  Time: {time_str}\n"
        f"  Date: {date_str}\n"
        "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"
    )

    if not os.path.isdir(Config.TEMP_DIR):
        os.makedirs(Config.TEMP_DIR)
        
    required_file_name = os.path.join(Config.TEMP_DIR, f"time_{event.sender_id}.webp")
    
    img = Image.new("RGBA", (350, 220), color=(0, 0, 0, 115))
    
    try:
        fnt = ImageFont.truetype(FONT_FILE_TO_USE, 30)
    except:
        fnt = ImageFont.load_default()

    drawn_text = ImageDraw.Draw(img)
    drawn_text.text((10, 10), current_time, font=fnt, fill=(255, 255, 255))
    img.save(required_file_name)
    
    await event.client.send_file(
        event.chat_id,
        required_file_name,
        reply_to=reply_msg_id,
    )
    os.remove(required_file_name)
    await event.delete()