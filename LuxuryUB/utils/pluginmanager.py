import importlib
import sys
from pathlib import Path

from LuxuryUB import CMD_HELP, LOAD_PLUG

from ..Config import Config
from ..core import LOADED_CMDS, PLG_INFO
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..core.session import luxur
from ..helpers.tools import media_type
from ..helpers.utils import _cattools, _catutils, _format, install_pip, reply_id
from .decorators import admin_cmd, sudo_cmd

# تحديث اسم اللوغر لـ Luxury
LOGS = logging.getLogger("LuxuryUB")

def load_module(shortname, plugin_path=None):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        path = Path(f"LuxuryUB/plugins/{shortname}.py")
        checkplugins(path)
        name = "LuxuryUB.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        LOGS.info("💎 LuxuryUB: تم تحميل " + shortname)
    else:
        if plugin_path is None:
            path = Path(f"LuxuryUB/plugins/{shortname}.py")
            name = f"LuxuryUB.plugins.{shortname}"
        else:
            path = Path((f"{plugin_path}/{shortname}.py"))
            name = f"{plugin_path}/{shortname}".replace("/", ".")
        
        checkplugins(path)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        
        # ربط الكلاسات الجديدة LuxuryClient
        mod.bot = luxur
        mod.LOGS = LOGS
        mod.Config = Config
        mod._format = _format
        mod.tgbot = luxur.tgbot
        mod.sudo_cmd = sudo_cmd
        mod.CMD_HELP = CMD_HELP
        mod.reply_id = reply_id
        mod.admin_cmd = admin_cmd
        mod._catutils = _catutils
        mod._cattools = _cattools
        mod.media_type = media_type
        mod.edit_delete = edit_delete
        mod.install_pip = install_pip
        mod.parse_pre = _format.parse_pre
        mod.edit_or_reply = edit_or_reply
        mod.logger = logging.getLogger(shortname)
        mod.borg = luxur
        
        spec.loader.exec_module(mod)
        sys.modules["LuxuryUB.plugins." + shortname] = mod
        LOGS.info("💎 LuxuryUB: تم تحميل ✓ " + shortname)

def remove_plugin(shortname):
    try:
        cmd = []
        if shortname in PLG_INFO:
            cmd += PLG_INFO[shortname]
        else:
            cmd = [shortname]
        for cmdname in cmd:
            if cmdname in LOADED_CMDS:
                for i in LOADED_CMDS[cmdname]:
                    luxur.remove_event_handler(i)
                del LOADED_CMDS[cmdname]
        return True
    except Exception as e:
        LOGS.error(e)
    
    try:
        for i in LOAD_PLUG[shortname]:
            luxur.remove_event_handler(i)
        del LOAD_PLUG[shortname]
    except: pass
    
    try:
        name = f"LuxuryUB.plugins.{shortname}"
        for i in reversed(range(len(luxur._event_builders))):
            ev, cb = luxur._event_builders[i]
            if cb.__module__ == name:
                del luxur._event_builders[i]
    except: raise ValueError

def checkplugins(filename):
    """دالة التصحيح التلقائي لملفات لوكجوري"""
    with open(filename, "r") as f:
        filedata = f.read()
    
    # تحويل الدوال القديمة للجديدة لتعمل مع نظام Luxury المتطور
    filedata = filedata.replace("sendmessage", "send_message")
    filedata = filedata.replace("sendfile", "send_file")
    filedata = filedata.replace("editmessage", "edit_message")
    
    with open(filename, "w") as f:
        f.write(filedata)

def start_assistant(shortname):
    """تحميل ملفات البوت المساعد بمسار Luxury الصحيح"""
    if shortname.startswith("__"):
        return
    
    path = Path(f"LuxuryUB/assistant/{shortname}.py")
    name = "LuxuryUB.assistant.{}".format(shortname)
    
    if not path.exists():
        return
        
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    
    if not shortname.endswith("_"):
        mod.tgbot = luxur.tgbot
        mod.bot = luxur
        
    spec.loader.exec_module(mod)
    sys.modules[name] = mod
    print(f"💎 Luxury Assistant: تم تحميل {shortname}")