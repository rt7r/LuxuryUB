import time
from .Config import Config
from .core.logger import logging
from .core.session import luxur
from .sql_helper.globals import addgvar, delgvar, gvarstatus

__version__ = "1.0.0" 
__license__ = "كـتابة وتـعديل فريـق لوكجوري"
__author__ = "Luxury Team <https://t.me/ee2en>"
__copyright__ = "Luxury TEAM (C) 2024 - 2026 " + __author__  

luxur.version = __version__
luxur.tgbot.version = __version__
LOGS = logging.getLogger("Luxury")
bot = luxur

StartTime = time.time()
LUXURY_VERSION = "1.0.0"

if Config.UPSTREAM_REPO == "Abod20112011":
    UPSTREAM_REPO_URL = "https://github.com/rt7r/LuxuryUB"
else:
    UPSTREAM_REPO_URL = Config.UPSTREAM_REPO

if Config.PRIVATE_GROUP_BOT_API_ID == 0:
    if gvarstatus(Config.OWNER_ID, "PRIVATE_GROUP_BOT_API_ID") is None:
        Config.BOTLOG = False
        Config.BOTLOG_CHATID = "me"
    else:
        Config.BOTLOG_CHATID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
        Config.PRIVATE_GROUP_BOT_API_ID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
        Config.BOTLOG = True
else:
    if str(Config.PRIVATE_GROUP_BOT_API_ID)[0] != "-":
        Config.BOTLOG_CHATID = int("-" + str(Config.PRIVATE_GROUP_BOT_API_ID))
    else:
        Config.BOTLOG_CHATID = Config.PRIVATE_GROUP_BOT_API_ID
    Config.BOTLOG = True

if Config.PM_LOGGER_GROUP_ID == 0:
    if gvarstatus(Config.OWNER_ID, "PRIVATE_GROUP_BOT_API_ID") is None:
        Config.PM_LOGGER_GROUP_ID = -100
    else:
        Config.PM_LOGGER_GROUP_ID = int(gvarstatus("PM_LOGGER_GROUP_ID"))
elif str(Config.PM_LOGGER_GROUP_ID)[0] != "-":
    Config.PM_LOGGER_GROUP_ID = int("-" + str(Config.PM_LOGGER_GROUP_ID))

HEROKU_APP = None

# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
CMD_LIST = {}
SUDO_LIST = {}
INT_PLUG = ""
LOAD_PLUG = {}

# Variables
BOTLOG = Config.BOTLOG
BOTLOG_CHATID = Config.BOTLOG_CHATID
PM_LOGGER_GROUP_ID = Config.PM_LOGGER_GROUP_ID