"""
بحث يوتيوب انلاين - سورس لوكجوري
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
الأمر: .بحث <اسم المقطع>
ضعه في: LuxuryUB/plugins/youtube_search.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import asyncio
import os
import re
import secrets
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import yt_dlp
from telethon import Button, types
from telethon.errors import MessageNotModifiedError, QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo

from LuxuryUB import luxur
from ..Config import Config
from ..core.decorators import check_owner

# ── deno في PATH ──────────────────────────────────────────
_ROOT = os.path.abspath(".")
if _ROOT not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _ROOT + os.pathsep + os.environ.get("PATH", "")

COOKIE_PATH = "cookies.txt"
HAS_COOKIES = os.path.exists(COOKIE_PATH)
HAS_DENO    = os.path.exists(os.path.join(_ROOT, "deno"))
DL_DIR      = "downloads"
os.makedirs(DL_DIR, exist_ok=True)

_MENU_THUMB = "https://placehold.co/200x50/0d0d0d/0d0d0d.jpg"


_CACHE: dict = {}
_CACHE_MAX = 30

def _cache_set(key: str, value: dict) -> None:
    _CACHE[key] = value
    if len(_CACHE) > _CACHE_MAX:
        for old in list(_CACHE.keys())[: len(_CACHE) - _CACHE_MAX]:
            _CACHE.pop(old, None)

_executor = ThreadPoolExecutor(max_workers=3)


def _search_sync(query: str, limit: int) -> list:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            return [e for e in (info or {}).get("entries", []) if e and e.get("id")]
    except Exception as e:
        print(f"[YTS] Search error: {e}")
        return []


async def _search(query: str, limit: int = 10) -> list:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _search_sync, query, limit)


def _fmt_duration(secs) -> str:
    if not secs:
        return "غير معروف"
    s = int(secs)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def _fmt_views(n) -> str:
    if not n:
        return "غير معروف"
    n = int(n)
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def _fmt_date(d, timestamp=None) -> str:
    s = str(d or "")
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}/{s[4:6]}/{s[6:]}"
    if timestamp:
        try:
            from datetime import datetime, timezone
            dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
            return dt.strftime("%Y/%m/%d")
        except Exception:
            pass
    return "غير معروف"


def _safe(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _thumb_url(video: dict) -> str:
    return f"https://i.ytimg.com/vi/{video.get('id','')}/hqdefault.jpg"


def _caption(video: dict, page: int, total: int) -> str:
    vid    = video.get("id", "")
    url    = f"https://www.youtube.com/watch?v={vid}"
    title  = _safe(video.get("title", "بدون عنوان"))
    dur    = _fmt_duration(video.get("duration"))
    views  = _fmt_views(video.get("view_count"))
    date   = _fmt_date(
        video.get("upload_date"),
        video.get("release_timestamp") or video.get("timestamp"),
    )
    ch     = _safe(video.get("channel") or video.get("uploader") or "غير معروف")
    ch_url = video.get("channel_url", "")

    out  = f'🎥 <b><a href="{url}">{title}</a></b>\n\n'
    out += f"⏱ <b>المدة:</b> <code>{dur}</code>  |  "
    out += f"👁 <b>المشاهدات:</b> <code>{views}</code>\n"
    if date != "غير معروف":
        out += f"📅 <b>الرفع:</b> <code>{date}</code>\n"
    out += (f'📢 <b>القناة:</b> <a href="{ch_url}">{ch}</a>\n' if ch_url
            else f"📢 <b>القناة:</b> {ch}\n")
    out += f"\n📄 <b>{page} / {total}</b>"
    return out


def _dl_caption(emoji: str, title: str, bot_usr: str) -> str:

    return (
        f"<blockquote>Download Done {emoji}</blockquote>\n"
        f"By: {bot_usr} "
    )



def _nav_btns(key: str, page: int, total: int, vid_id: str) -> list:
    prev_p = total if page == 1 else page - 1
    next_p = 1 if page == total else page + 1
    return [
        [
            Button.inline("⬅️ السابق",         data=f"yts_p_{key}_{prev_p}"),
            Button.inline(f"📄 {page}/{total}", data="yts_pg"),
            Button.inline("التالي ➡️",          data=f"yts_p_{key}_{next_p}"),
        ],
        [
            Button.inline("فيديو 🎬", data=f"yts_v_{key}_{vid_id}_{page}"),
            Button.inline("القائمة 🗂",      data=f"yts_m_{key}_{page}"),
            Button.inline("صوت 🎵",   data=f"yts_a_{key}_{vid_id}_{page}"),
        ],
    ]


def _menu_text(videos: list) -> str:
    lines = ["📋 <b>نتائج البحث — اختر رقماً:</b>\n"]
    for i, v in enumerate(videos, 1):
        title = _safe(v.get("title", "بدون عنوان"))[:55]
        dur   = _fmt_duration(v.get("duration"))
        lines.append(f"<b>{i}.</b> {title} <code>[{dur}]</code>")
    return "\n".join(lines)


def _menu_btns(key: str, total: int, back_page: int) -> list:
    rows, row = [], []
    for i in range(1, total + 1):
        row.append(Button.inline(str(i), data=f"yts_p_{key}_{i}"))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([Button.inline("🔙 رجوع", data=f"yts_p_{key}_{back_page}")])
    return rows


@luxur.ar_cmd(
    pattern=r"بحث (.*)",
    command=("بحث", "misc"),
    info="بحث يوتيوب انلاين\n`.بحث <اسم المقطع>`",
)
async def user_search_cmd(event):
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.edit("⚠️ اكتب اسم المقطع بعد الأمر.\nمثال: `.بحث فيروز`")

    bot_username = Config.TG_BOT_USERNAME
    if not bot_username:
        return await event.edit("⚠️ `TG_BOT_USERNAME` غير جاهز، انتظر ثانية وأعد.")

    _CACHE[f"pending_{Config.OWNER_ID}"] = event.chat_id

    await event.edit("🔍 جاري البحث...")
    try:
        results = await event.client.inline_query(bot_username, f"yts {query}")
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
            await event.delete()
        else:
            await event.edit("❌ لم يرجع البوت نتائج.\nتأكد من تفعيل الانلاين للبوت عبر @BotFather.")
    except Exception as e:
        await event.edit(f"❌ خطأ:\n`{e}`")



@luxur.tgbot.on(InlineQuery)
async def bot_inline_yts(event):
    q = (event.text or "").strip()
    if not q.startswith("yts "):
        return

    query  = q[4:].strip()
    client = event.client

    videos = await _search(query, limit=10)
    if not videos:
        await event.answer(
            [event.builder.article(title="❌ لا نتائج", text=f"لم أجد نتائج لـ: {query}")]
        )
        return

    key     = secrets.token_hex(4)
    total   = len(videos)
    chat_id = _CACHE.pop(f"pending_{Config.OWNER_ID}", Config.OWNER_ID)
    _cache_set(key, {"results": videos, "chat_id": chat_id})

    inline_results = []
    for i, video in enumerate(videos):
        page    = i + 1
        vid_id  = video.get("id", "")
        caption = _caption(video, page, total)
        buttons = _nav_btns(key, page, total, vid_id)
        thumb   = _thumb_url(video)

        markup         = client.build_reply_markup(buttons)
        thumb_doc      = types.InputWebDocument(url=thumb, size=0, mime_type="image/jpeg", attributes=[])
        text, entities = await client._parse_message_text(caption, "html")

        inline_results.append(
            types.InputBotInlineResult(
                id=str(uuid4()),
                type="photo",
                title=_safe(video.get("title", f"نتيجة {page}")),
                description=f"⏱ {_fmt_duration(video.get('duration'))}  |  👁 {_fmt_views(video.get('view_count'))}",
                url=f"https://www.youtube.com/watch?v={vid_id}",
                thumb=thumb_doc,
                content=thumb_doc,
                send_message=types.InputBotInlineMessageMediaAuto(
                    reply_markup=markup,
                    message=text,
                    entities=entities,
                ),
            )
        )

    try:
        await event.answer(inline_results, cache_time=0)
    except QueryIdInvalidError:
        pass



@luxur.tgbot.on(CallbackQuery(data=re.compile(rb"^yts_p_([a-f0-9]{8})_(\d+)$")))
@check_owner
async def on_yts_page(c_q):
    key  = c_q.data_match.group(1).decode()
    page = int(c_q.data_match.group(2).decode())

    cache = _CACHE.get(key)
    if not cache:
        return await c_q.answer("⚠️ انتهت جلسة البحث، ابحث مجدداً.", alert=True)

    videos = cache["results"]
    total  = len(videos)
    page   = max(1, min(page, total))
    video  = videos[page - 1]
    vid_id = video.get("id", "")

    try:
        await c_q.edit(
            text=_caption(video, page, total),
            file=_thumb_url(video),
            buttons=_nav_btns(key, page, total, vid_id),
            parse_mode="html",
        )
    except MessageNotModifiedError:
        pass


@luxur.tgbot.on(CallbackQuery(data=re.compile(rb"^yts_m_([a-f0-9]{8})_(\d+)$")))
@check_owner
async def on_yts_menu(c_q):
    key     = c_q.data_match.group(1).decode()
    back_pg = int(c_q.data_match.group(2).decode())

    cache = _CACHE.get(key)
    if not cache:
        return await c_q.answer("⚠️ انتهت جلسة البحث.", alert=True)

    videos = cache["results"]
    try:
        await c_q.edit(
            text=_menu_text(videos),
            file=_MENU_THUMB,
            buttons=_menu_btns(key, len(videos), back_pg),
            parse_mode="html",
        )
    except MessageNotModifiedError:
        pass


@luxur.tgbot.on(CallbackQuery(data=b"yts_pg"))
@check_owner
async def on_yts_pg(c_q):
    await c_q.answer("استخدم أزرار التنقل ⬅️ ➡️")



@luxur.tgbot.on(CallbackQuery(data=re.compile(rb"^yts_(v|a)_([a-f0-9]{8})_([A-Za-z0-9_\-]{6,15})_(\d+)$")))
@check_owner
async def on_yts_download(c_q):
    dl_type  = c_q.data_match.group(1).decode()
    key      = c_q.data_match.group(2).decode()
    vid_id   = c_q.data_match.group(3).decode()
    page     = int(c_q.data_match.group(4).decode())
    is_audio = dl_type == "a"
    emoji    = "🎵" if is_audio else "🎬"

    cache   = _CACHE.get(key)
    total   = len(cache["results"]) if cache else 1
    chat_id = cache.get("chat_id", Config.OWNER_ID) if cache else Config.OWNER_ID
    bot_usr = Config.TG_BOT_USERNAME or ""

    await c_q.answer(f"⏳ جاري التحميل {emoji}...")
    try:
        await c_q.edit(buttons=[[Button.inline(f"⏳ جاري التحميل {emoji}", data="yts_pg")]])
    except Exception:
        pass

    result = await asyncio.get_event_loop().run_in_executor(
        _executor, _download_sync, vid_id, is_audio
    )
    file_path, size_mb, title, performer, duration, thumb_path = result

    if not file_path or not os.path.exists(file_path):
        if cache:
            try:
                v = cache["results"][page - 1]
                await c_q.edit(
                    text=_caption(v, page, total),
                    file=_thumb_url(v),
                    buttons=_nav_btns(key, page, total, vid_id),
                    parse_mode="html",
                )
            except Exception:
                pass
        return await c_q.answer("❌ فشل التحميل، المقطع محمي أو محذوف.", alert=True)

    try:
        await c_q.edit(buttons=[[Button.inline(f"🚀 جاري الرفع {emoji}", data="yts_pg")]])
    except Exception:
        pass

    caption = _dl_caption(emoji, title, bot_usr)

    try:
        if is_audio:
            attrs = [DocumentAttributeAudio(
                duration=int(duration or 0),
                voice=False,
                title=(title or "") or None,
                performer=(performer or "") or None,
            )]
            await luxur.send_file(
                chat_id,
                file_path,
                caption=caption,
                parse_mode="html",
                thumb=thumb_path,
                attributes=attrs,
            )
        else:
            attrs = [DocumentAttributeVideo(
                duration=int(duration or 0),
                w=1280, h=720,
                supports_streaming=True,
            )]
            await luxur.send_file(
                chat_id,
                file_path,
                caption=caption,
                parse_mode="html",
                thumb=thumb_path,
                attributes=attrs,
                supports_streaming=True,
            )
    except Exception as e:
        print(f"[YTS] Upload error: {e}")
    finally:
        for p in (file_path, thumb_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    if cache:
        try:
            v = cache["results"][page - 1]
            await c_q.edit(
                text=_caption(v, page, total),
                file=_thumb_url(v),
                buttons=_nav_btns(key, page, total, vid_id),
                parse_mode="html",
            )
        except Exception:
            pass


def _download_sync(video_id: str, is_audio: bool) -> tuple:
    url      = f"https://www.youtube.com/watch?v={video_id}"
    out_name = secrets.token_hex(8)

    attack_clients = ["web"] if HAS_COOKIES else ["tv_embedded", "ios", "android"]

    base = {
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": attack_clients}},
        "cookiefile": COOKIE_PATH if HAS_COOKIES else None,
    }
    if HAS_DENO:
        base["javascript_engine"] = "deno"

    if is_audio:
        opts = {
            **base,
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DL_DIR, f"{out_name}.%(ext)s"),
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
            ],
        }
    else:
        opts = {
            **base,
            "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
            "outtmpl": os.path.join(DL_DIR, f"{out_name}.%(ext)s"),
            "merge_output_format": "mp4",
        }

    opts = {k: v for k, v in opts.items() if v is not None}

    title      = None
    performer  = None
    duration   = 0
    thumb_path = None

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info      = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            title     = info.get("title", "")
            performer = info.get("channel") or info.get("uploader") or ""
            duration  = info.get("duration") or 0
            thumb_url = info.get("thumbnail", "")
            thumb_path = _dl_thumb(thumb_url, out_name)

            if not os.path.exists(file_path):
                for f in os.listdir(DL_DIR):
                    if f.startswith(out_name) and not f.endswith(("_thumb.jpg", "_thumb.webp")):
                        file_path = os.path.join(DL_DIR, f)
                        break

            size_mb = os.path.getsize(file_path) / (1024 * 1024) if os.path.exists(file_path) else 0
            return file_path, size_mb, title, performer, duration, thumb_path

    except Exception as e:
        print(f"[YTS] Download error: {e}")
        return None, 0, title, performer, duration, thumb_path


def _dl_thumb(thumb_url: str, out_name: str) -> str | None:
    if not thumb_url:
        return None
    try:
        path = os.path.join(DL_DIR, f"{out_name}_thumb.jpg")
        urllib.request.urlretrieve(thumb_url, path)
        return path if os.path.exists(path) else None
    except Exception:
        return None

