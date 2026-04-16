import sys
from LuxuryUB.core.logger import logging
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession
from telethon.errors import AccessTokenExpiredError, AccessTokenInvalidError
from ..Config import Config
from .alLuxuryUB import luxury_session_setup
from .client import LuxuryClient

LOGS = logging.getLogger("Luxury")

__version__ = "1.0.0" 

loop = None

if Config.STRING_SESSION:
    session = luxury_session_setup(Config.STRING_SESSION, LOGS)
else:
    session = "LuxuryUB"

try:
    luxur = LuxuryClient(
        session=session,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        loop=loop,
        app_version=__version__,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    )
except Exception as e:
    print(f"[ERROR] - فشل تشغيل الحساب الرئيسي: {str(e)}")
    sys.exit()

try:
    luxur.tgbot = LuxuryClient(
        session="LuxuryTgbot",
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        loop=loop,
        app_version=__version__,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    ).start(bot_token=Config.TG_BOT_TOKEN)
except AccessTokenExpiredError:
    LOGS.error("⚠️ توكن البوت منتهي الصلاحية! قم باستبداله ليعمل سورس لوكجوري.")
except AccessTokenInvalidError:
    LOGS.error("⚠️ توكن البوت غير صحيح! تأكد من التوكن من @BotFather.")
except Exception as e:
    LOGS.error(f"❌ خطأ في تشغيل توكن البوت: {str(e)}")