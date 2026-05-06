import os
import random
import asyncio
import re
from contextlib import contextmanager
from yt_dlp import YoutubeDL
from telethon import events, functions
from pytgcalls import PyTgCalls, filters
from pytgcalls.types import MediaStream, VideoQuality, AudioQuality
from LuxuryUB import luxur
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..sql_helper.globals import gvarstatus, addgvar


cookie_path = "cookies.txt"
has_cookies = os.path.exists(cookie_path)

if has_cookies:
    attack_clients = ["web"]
else:
    attack_clients = ["tv_embedded", "ios"]

os.environ["PATH"] += os.pathsep + os.path.abspath(".")

_YTDLP_CACHE = os.path.abspath(".ytdlp_cache")
os.makedirs(_YTDLP_CACHE, exist_ok=True)

_DL_DIR = os.path.abspath(".luxury_downloads")
os.makedirs(_DL_DIR, exist_ok=True)

YDL_COMMON = {
    "extractor_args": {"youtube": {"player_client": attack_clients}},
    "concurrent_fragment_downloads": 10,
    "http_chunk_size": 10485760,
    "socket_timeout": 8,
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "source_address": "0.0.0.0",
    "default_search": "ytsearch",
    "skip_download": True,
    "cachedir": _YTDLP_CACHE,
    "cookiefile": cookie_path if has_cookies else None,
}

YDL_AUDIO_OPTS = {**YDL_COMMON, "format": "bestaudio[ext=m4a]/bestaudio/best"}
YDL_VIDEO_OPTS = {
    **YDL_COMMON,
    "format": "best[height<=480]/best",
    "merge_output_format": "mp4",
}

_ydl_audio = YoutubeDL(YDL_AUDIO_OPTS)
_ydl_video = YoutubeDL(YDL_VIDEO_OPTS)

active_calls = {}
is_playing = {}
playlist = {}
authorized_users = {}
current_local_file = {}

_chat_locks = {}
_owner_locks = {}

PYTGCALLS_TIMEOUT = 25


def _chat_lock(chat_id):
    if chat_id not in _chat_locks:
        _chat_locks[chat_id] = asyncio.Lock()
    return _chat_locks[chat_id]


def _owner_lock(owner_id):
    if owner_id not in _owner_locks:
        _owner_locks[owner_id] = asyncio.Lock()
    return _owner_locks[owner_id]


async def _safe_call(coro_factory, *, default=None):
    """ينفذ عملية pytgcalls بمهلة. يرجع default إذا تجمد أو فشل."""
    try:
        return await asyncio.wait_for(coro_factory(), timeout=PYTGCALLS_TIMEOUT)
    except asyncio.TimeoutError:
        return ("__timeout__", default)
    except Exception as e:
        return ("__error__", e)


@contextmanager
def _disguise_as_telethon(client):
    """
    يخدع فحص py-tgcalls v2.x اللي يفحص:
        str(obj.__class__.__module__).split('.')[0] in ('telethon','pyrogram','hydrogram')
    العملية مزامنة بحتة — لا حدث async بينها.
    """
    cls = client.__class__
    old_module = cls.__module__
    old_name = cls.__name__
    try:
        cls.__module__ = "telethon.client.telegramclient"
        cls.__name__ = "TelegramClient"
        yield
    finally:
        cls.__module__ = old_module
        cls.__name__ = old_name


def _build_stream(source: str, is_video: bool) -> MediaStream:
    """يبني MediaStream متوافق مع py-tgcalls v2.2.x."""
    if is_video:
        return MediaStream(
            source,
            video_parameters=VideoQuality.SD_480p,
            audio_parameters=AudioQuality.HIGH,
        )
    return MediaStream(
        source,
        audio_parameters=AudioQuality.HIGH,
        video_flags=MediaStream.Flags.IGNORE,
    )


async def _extract(search_query: str, is_video: bool):
    """يشغل yt-dlp في thread منفصل حتى ما يجمد الـ event loop."""
    if not search_query.startswith("http"):
        search_query = f"ytsearch1:{search_query}"
    ydl = _ydl_video if is_video else _ydl_audio
    info = await asyncio.to_thread(ydl.extract_info, search_query, False)
    if info and "entries" in info and info["entries"]:
        info = info["entries"][0]
    return info


def _get_file_title(reply):
    """يستخرج اسم الملف الحقيقي من رسالة تيلثون."""
    media = reply.audio or reply.video or reply.voice
    if media:
        for attr in (getattr(media, "attributes", None) or []):
            cls_name = attr.__class__.__name__
            if cls_name == "DocumentAttributeAudio":
                title = getattr(attr, "title", None)
                if title:
                    perf = getattr(attr, "performer", None)
                    return f"{perf} - {title}" if perf else title
            if cls_name == "DocumentAttributeFilename":
                fn = getattr(attr, "file_name", None)
                if fn:
                    return os.path.splitext(fn)[0]
    if getattr(reply, "file", None) and getattr(reply.file, "name", None):
        return os.path.splitext(reply.file.name)[0]
    if reply.voice:
        return "رسالة صوتية 🎤"
    return "ملف مرفق 📁"


def _cleanup_local(chat_id):
    """يحذف الملف المحلي المُشغّل سابقاً لهذي المحادثة."""
    old = current_local_file.pop(chat_id, None)
    _delete_file(old)


def _delete_file(path):
    """يحذف ملف بأمان دون رمي استثناء."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass


def _swap_local(chat_id, new_path_or_none):
    """
    يستبدل الملف المُسجّل للمحادثة بالجديد ويرجع الملف القديم (للحذف لاحقاً
    بعد ما يبدأ البث الجديد فعلياً، حتى ما نقطع ffmpeg وهو يقرأ).
    """
    old = current_local_file.pop(chat_id, None)
    if new_path_or_none:
        current_local_file[chat_id] = new_path_or_none
    return old


def is_music_enabled(owner_id):
    return gvarstatus(owner_id, "MUSIC_STATUS") == "true"


@luxur.ar_cmd(pattern="(تفعيل|تعطيل) الميوزك$")
async def toggle_music(event):
    owner_id = (await event.client.get_me()).id
    status = "true" if "تفعيل" in event.text else "false"
    addgvar(owner_id, "MUSIC_STATUS", status)
    await edit_or_reply(
        event,
        f"**💎 تم {'تفعيل' if status=='true' else 'تعطيل'} نظام الميوزك بنجاح ✓**",
    )


@luxur.ar_cmd(pattern=r"دعوة(?:\s|$)([\s\S]*)")
async def invite_vc(event):
    reply = await event.get_reply_message()
    target = event.pattern_match.group(1).strip()
    if not target and not reply:
        return await edit_delete(event, "**⚠️ يرجى الرد على شخص أو كتابة معرفه للدعوة.**")
    user = reply.sender_id if reply else target
    proc = await edit_or_reply(event, "**💎 جاري إرسال الدعوة...**")
    try:
        full_chat = await event.client(
            functions.channels.GetFullChannelRequest(event.chat_id)
        )
        call_obj = full_chat.full_chat.call
        if not call_obj:
            return await proc.edit("**⚠️ لا توجد مكالمة نشطة لدعوته إليها.**")
        await event.client(
            functions.phone.InviteToGroupCallRequest(call=call_obj, users=[user])
        )
        await proc.edit("**✅ تم إرسال الدعوة بنجاح.**")
    except Exception as e:
        err = str(e).lower()
        if "already a participant" in err or "already in" in err:
            await proc.edit("**ℹ️ هذا الشخص موجود بالاتصال أصلاً.**")
        else:
            await proc.edit(f"**❌ فشل إرسال الدعوة:** `{e}`")


MUSIC_CMDS = (
    "(شغل 1|شغل فيديو|شغل|تشغيل|فيديو 1|فيديو|انضمام|مغادرة|افتح مكالمة|"
    "اطفاء مكالمة|حالة المكالمة|تخطي|وكف مؤقتا|وكف|وقف|كمل|استمرار|"
    "ايقاف نهائي|ايقاف|قائمة التشغيل)"
)


async def _ensure_call(event):
    """يضمن وجود PyTgCalls instance لصاحب البوت ويسجل الـ stream-end handler."""
    owner_id = (await event.client.get_me()).id

    async with _owner_lock(owner_id):
        if owner_id in active_calls:
            return active_calls[owner_id], owner_id

        with _disguise_as_telethon(event.client):
            call_obj = PyTgCalls(event.client)

        await call_obj.start()

        @call_obj.on_update(filters.stream_end())
        async def auto_play_handler(client, update):
            cid = update.chat_id
            _cleanup_local(cid)

            async with _chat_lock(cid):
                if cid in playlist and playlist[cid]:
                    nxt = playlist[cid].pop(0)
                    res = await _safe_call(
                        lambda: client.play(
                            cid, _build_stream(nxt["url"], nxt["is_video"])
                        )
                    )
                    if isinstance(res, tuple) and res[0] in ("__timeout__", "__error__"):
                        is_playing[cid] = False
                        await event.client.send_message(
                            cid,
                            f"**⚠️ تم تخطي المقطع بسبب خطأ:** `{res[1]}`",
                        )
                        return
                    is_playing[cid] = True
                    if not str(nxt["url"]).startswith("http"):
                        current_local_file[cid] = nxt["url"]
                    await event.client.send_message(
                        cid,
                        f"**⏭️ التشغيل التلقائي:**\nيتم الآن بث `{nxt['title']}` 💎",
                    )
                else:
                    is_playing[cid] = False
                    await _safe_call(lambda: client.leave_call(cid))

        active_calls[owner_id] = call_obj
        return call_obj, owner_id


async def process_music_command(event, cmd, target_id_str, query, reply):
    owner_id = (await event.client.get_me()).id
    if not is_music_enabled(owner_id):
        return await event.reply("**⚠️ نظام الميوزك معطل حالياً.**")

    chat_id = int(target_id_str) if target_id_str else event.chat_id
    call, owner_id = await _ensure_call(event)

    async with _chat_lock(chat_id):
        return await _handle_music_cmd(event, cmd, chat_id, query, reply, call)


async def _handle_music_cmd(event, cmd, chat_id, query, reply, call):

    if cmd == "افتح مكالمة":
        try:
            await event.client(
                functions.phone.CreateGroupCallRequest(
                    peer=chat_id, random_id=random.randint(10000, 999999999)
                )
            )
            return await event.reply("**✅ تم فتح المكالمة الصوتية.**")
        except Exception:
            return await event.reply("**⚠️ المكالمة مفتوحة بالفعل.**")

    if cmd == "اطفاء مكالمة":
        try:
            full_chat = await event.client(
                functions.channels.GetFullChannelRequest(chat_id)
            )
            if full_chat.full_chat.call:
                await event.client(
                    functions.phone.DiscardGroupCallRequest(
                        call=full_chat.full_chat.call
                    )
                )
                # نظف حالة pytgcalls الداخلية للمحادثة حتى ما تبقى عالقة
                await _safe_call(lambda: call.leave_call(chat_id))
                is_playing[chat_id] = False
                if chat_id in playlist:
                    playlist[chat_id].clear()
                _cleanup_local(chat_id)
                return await event.reply("**❌ تم إنهاء المكالمة الصوتية.**")
            return await event.reply("**⚠️ لا توجد مكالمة نشطة.**")
        except Exception as e:
            return await event.reply(f"**❌ خطأ:** `{e}`")

    if cmd == "حالة المكالمة":
        try:
            full_chat = await event.client(
                functions.channels.GetFullChannelRequest(chat_id)
            )
            if not full_chat.full_chat.call:
                return await event.reply("**⚠️ لا توجد مكالمة نشطة هنا.**")
            info = await event.client(
                functions.phone.GetGroupCallRequest(
                    call=full_chat.full_chat.call, limit=1
                )
            )
            return await event.reply(
                f"**📊 حالة المكالمة :**\n"
                f"**العنوان:** `{info.call.title or 'لا يوجد'}`\n"
                f"**المشاركين:** `{info.call.participants_count}`"
            )
        except Exception as e:
            return await event.reply(f"**⚠️ خطأ:** `{e}`")

    if cmd == "انضمام":
        return await event.reply(
            "**✅ البوت ينضم للمكالمة تلقائياً عند طلب تشغيل المقطع!**"
        )

    if cmd in ["مغادرة", "ايقاف نهائي", "ايقاف"]:
        res = await _safe_call(lambda: call.leave_call(chat_id))
        is_playing[chat_id] = False
        if chat_id in playlist:
            playlist[chat_id].clear()
        _cleanup_local(chat_id)
        if isinstance(res, tuple) and res[0] == "__timeout__":
            return await event.reply(
                "**⏹️ تم تصفير الحالة (انتهت المهلة في المغادرة، الحالة محلياً نُظفت).**"
            )
        return await event.reply(
            "**⏹️ تم إيقاف التشغيل والمغادرة وتصفير القائمة.**"
        )

    if cmd in ["وكف مؤقتا", "وكف", "وقف"]:
        res = await _safe_call(lambda: call.pause(chat_id))
        if isinstance(res, tuple):
            return await event.reply(
                f"**⚠️ خطأ:** `{res[1] if res[0]=='__error__' else 'انتهت المهلة'}`"
            )
        return await event.reply("**⏸️ تم إيقاف التشغيل مؤقتاً.**")

    if cmd in ["كمل", "استمرار"]:
        res = await _safe_call(lambda: call.resume(chat_id))
        if isinstance(res, tuple):
            return await event.reply(
                f"**⚠️ خطأ:** `{res[1] if res[0]=='__error__' else 'انتهت المهلة'}`"
            )
        return await event.reply("**▶️ تم استئناف التشغيل.**")

    if cmd == "تخطي":
        if chat_id in playlist and playlist[chat_id]:
            nxt = playlist[chat_id].pop(0)
            new_local = nxt["url"] if not str(nxt["url"]).startswith("http") else None
            stream = _build_stream(nxt["url"], nxt["is_video"])
            res = await _safe_call(lambda: call.play(chat_id, stream))
            if isinstance(res, tuple):
                return await event.reply(
                    f"**⚠️ خطأ في التخطي:** `{res[1] if res[0]=='__error__' else 'انتهت المهلة'}`"
                )
            old = _swap_local(chat_id, new_local)
            _delete_file(old)
            is_playing[chat_id] = True
            return await event.reply(
                f"**⏭️ تم التخطي، يتم الآن تشغيل:** `{nxt['title']}`"
            )
        else:
            res = await _safe_call(lambda: call.leave_call(chat_id))
            is_playing[chat_id] = False
            _cleanup_local(chat_id)
            return await event.reply(
                "**⏹️ القائمة فارغة، تم إيقاف التشغيل والمغادرة.**"
            )

    if cmd == "قائمة التشغيل":
        if chat_id not in playlist or not playlist[chat_id]:
            return await event.reply("**📭 قائمة التشغيل فارغة.**")
        text = "**📑 قائمة التشغيل الحالية:**\n\n"
        for i, item in enumerate(playlist[chat_id], 1):
            text += f"**{i}.** `{item['title']}`\n"
        return await event.reply(text)

    if cmd in ["شغل", "تشغيل", "شغل 1", "فيديو", "شغل فيديو", "فيديو 1"]:
        proc = await event.reply("**💎 جاري معالجة الطلب وبدء البث ...**")
        is_video = "فيديو" in cmd or (reply and reply.video)
        is_force = "1" in cmd
        url_or_path = ""
        title = ""

        try:
            if reply and (reply.audio or reply.video or reply.voice):
                title = _get_file_title(reply)
                await proc.edit(f"**📥 جاري تحميل:** `{title}`")
                downloaded = await reply.download_media(file=_DL_DIR + os.sep)
                url_or_path = os.path.abspath(downloaded)

            elif query or (reply and reply.text):
                search_query = (query or reply.text).strip()
                await proc.edit(
                    f"**💎 جاري البحث واستخراج البيانات...**\n"
                    f"**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`"
                )
                info = await _extract(search_query, is_video)
                if not info:
                    return await proc.edit("**❌ لم يتم العثور على نتائج.**")

                url_or_path = info.get("url")
                if not url_or_path:
                    for f in (info.get("formats") or [])[::-1]:
                        if f.get("url") and f.get("acodec") != "none":
                            url_or_path = f["url"]
                            break
                title = info.get("title", "مقطع غير معروف")
            else:
                return await proc.edit(
                    "**⚠️ يرجى كتابة اسم الأغنية أو الرد على ملف.**"
                )

            if not url_or_path:
                return await proc.edit("**❌ فشل في استخراج رابط البث.**")

            is_local = not str(url_or_path).startswith("http")

            if is_force:
                if chat_id in playlist:
                    playlist[chat_id].clear()
                is_playing[chat_id] = False

            if is_playing.get(chat_id) and not is_force:
                playlist.setdefault(chat_id, []).append(
                    {"title": title, "url": url_or_path, "is_video": is_video}
                )
                return await proc.edit(
                    f"**⏳ تمت الإضافة إلى قائمة التشغيل:**\n`{title}`\n"
                    f"**الترتيب في الطابور:** `{len(playlist[chat_id])}`"
                )

            stream = _build_stream(url_or_path, is_video)
            res = await _safe_call(lambda: call.play(chat_id, stream))
            if isinstance(res, tuple):
                if is_local:
                    _delete_file(url_or_path)
                err_msg = res[1] if res[0] == "__error__" else "انتهت المهلة (jam)"
                return await proc.edit(f"**⚠️ فشل البث المباشر:** `{err_msg}`")

            old = _swap_local(chat_id, url_or_path if is_local else None)
            _delete_file(old)
            is_playing[chat_id] = True

            return await proc.edit(
                f"**🎶 يتم الآن تشغيل:**\n`{title}`\n"
                f"**نوع البث:** `{'فيديو 🎬' if is_video else 'صوت 🎵'}`"
            )

        except Exception as e:
            if "Sign in to confirm" in str(e):
                return await proc.edit(
                    "**❌ فشل بسبب حماية يوتيوب.**\n"
                    "**السبب:** ملف `cookies.txt` المرفوع منتهي الصلاحية أو تم حظره.\n"
                    "**الحل:** استخرج ملف كوكيز جديد بصيغة (Netscape) وارفعه للاستضافة."
                )
            return await proc.edit(f"**⚠️ خطأ:** `{e}`")


@luxur.ar_cmd(pattern=f"{MUSIC_CMDS}(?: -id (-\\d+|\\d+))?(?:\\s|$)([\\s\\S]*)")
async def owner_music_handler(event):
    cmd = event.pattern_match.group(1)
    target_id_str = event.pattern_match.group(2)
    query = (
        event.pattern_match.group(3).strip()
        if event.pattern_match.group(3)
        else None
    )
    reply = await event.get_reply_message()
    await process_music_command(event, cmd, target_id_str, query, reply)


@luxur.ar_cmd(pattern="(مشغل|حذف المشغلين)$")
async def manage_operators(event):
    owner_id = (await event.client.get_me()).id
    if owner_id not in authorized_users:
        authorized_users[owner_id] = set()
    if "حذف" in event.text:
        authorized_users[owner_id].clear()
        return await edit_or_reply(event, "**🗑️ تم حذف جميع المشغلين بنجاح.**")
    reply = await event.get_reply_message()
    if reply:
        authorized_users[owner_id].add(reply.sender_id)
        await edit_or_reply(
            event, f"**✅ تم إضافة `{reply.sender_id}` لقائمة المشغلين.**"
        )


@luxur.on(events.NewMessage(incoming=True))
async def operator_listener(event):
    owner_id = (await event.client.get_me()).id
    sender_id = event.sender_id
    if sender_id not in authorized_users.get(owner_id, set()):
        return
    text = event.raw_text.strip()
    match = re.match(
        f"^{MUSIC_CMDS}(?: -id (-\\d+|\\d+))?(?:\\s|$)([\\s\\S]*)", text
    )
    if match:
        cmd = match.group(1)
        target_id_str = match.group(2)
        query = match.group(3).strip() if match.group(3) else None
        reply = await event.get_reply_message()
        if cmd in ["مغادرة", "ايقاف نهائي", "اطفاء مكالمة"]:
            return await event.reply(
                "**⚠️ عذراً، لا تمتلك صلاحية لهذا الأمر.**"
            )
        await process_music_command(event, cmd, target_id_str, query, reply)


@luxur.ar_cmd(pattern=r"تسمية(?:\s|$)([\s\S]*)")
async def rename_call(event):
    new_name = event.pattern_match.group(1).strip()
    if not new_name:
        return await edit_or_reply(
            event,
            "**⚠️ يرجى كتابة الاسم الجديد مع الأمر!\n"
            "مثال: `.تسمية سهرة شباب`**",
        )
    try:
        full_chat = await event.client(
            functions.channels.GetFullChannelRequest(event.chat_id)
        )
        call_obj = full_chat.full_chat.call
        if not call_obj:
            return await edit_or_reply(
                event, "**⚠️ لا توجد مكالمة صوتية نشطة.**"
            )
        await event.client(
            functions.phone.EditGroupCallTitleRequest(
                call=call_obj, title=new_name
            )
        )
        await edit_or_reply(
            event,
            f"**✅ تم تغيير اسم المكالمة بنجاح إلى:** `{new_name}` 💎",
        )
    except Exception as e:
        await edit_or_reply(event, f"**⚠️ خطأ:** `{e}`")
