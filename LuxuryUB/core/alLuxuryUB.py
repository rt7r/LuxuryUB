# LuxuryUB - UserBot
# Powered by Luxury Team
# This file is a part of < https://github.com/rt7r/LuxuryUB >

import base64
import ipaddress
import os
import struct
import sys
from .logger import logging
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.sessions.string import _STRUCT_PREFORMAT, CURRENT_VERSION, StringSession

LOGS = logging.getLogger("Luxury")

_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}

def luxury_session_setup(session, logger=LOGS, _exit=True):
    """دالة فحص وتحويل كود الجلسة لسورس لوكجوري"""
    if session:
        if session.startswith(CURRENT_VERSION):
            if len(session.strip()) != 353:
                logger.error("⚠️ كود جلسة تليثون غير صحيح، تأكد من الكود عزيزي.")
                if _exit:
                    sys.exit()
            return StringSession(session)

        elif len(session) in _PYRO_FORM.keys():
            try:
                data_ = struct.unpack(
                    _PYRO_FORM[len(session)],
                    base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
                )
                if len(session) in [351, 356]:
                    auth_id = 2
                else:
                    auth_id = 3
                dc_id, auth_key = data_[0], data_[auth_id]
                return StringSession(
                    CURRENT_VERSION
                    + base64.urlsafe_b64encode(
                        struct.pack(
                            _STRUCT_PREFORMAT.format(4),
                            dc_id,
                            ipaddress.ip_address(DC_IPV4[dc_id]).packed,
                            443,
                            auth_key,
                        )
                    ).decode("ascii")
                )
            except Exception as e:
                logger.error(f"❌ خطأ أثناء تحويل كود بايروجرام: {e}")
                if _exit:
                    sys.exit()
        else:
            logger.error("⚠️ كود الجلسة غير مدعوم أو غير صحيح، يرجى استخراج كود جديد.")
            if _exit:
                sys.exit()
                
    logger.error("❌ لم يتم العثور على كود الجلسة (STRING_SESSION).")
    if _exit:
        sys.exit()