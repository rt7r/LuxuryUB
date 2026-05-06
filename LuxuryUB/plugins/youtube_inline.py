import re
from telethon import events
from telethon.tl.custom import Button
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

from LuxuryUB.Config import Config
from LuxuryUB.core.managers import gvarstatus, addgvar
from LuxuryUB import luxur

from .yt_engine import yt_fast_search, yt_secure_download 

# ==========================================
# RAM Cache
# ==========================================
YT_SEARCH_CACHE = {}
YT_CHAT_CACHE = {} 

# ==========================================
# Helper Functions
# ==========================================

async def ensure_bot_is_admin(user_client):
    """تقوم بترقية البوت المساعد لأدمن في كروب التخزين لمرة واحدة فقط"""
    is_admin = gvarstatus("yt_bot_admin_status")
    if not is_admin:
        # جلب ايدي الكروب من الداتا بيز لأن قيمته في الكونفج 0
        dump_group = gvarstatus("PRIVATE_GROUP_BOT_API_ID") or Config.PRIVATE_GROUP_BOT_API_ID
        bot_username = Config.BOT_USERNAME

        if not dump_group or dump_group == 0 or not bot_username:
            print("⚠️ يوتيوب انلاين: لم يتم إعداد كروب التخزين أو يوزر البوت المساعد.")
            return

        try:
            rights = ChatAdminRights(
                post_messages=True, edit_messages=True, delete_messages=True
            )
            await user_client(EditAdminRequest(
                channel=int(dump_group),
                user_id=bot_username,
                admin_rights=rights,
                rank="YT Storage"
            ))
            addgvar("yt_bot_admin_status", "True")
            print("✅ تم رفع البوت المساعد كأدمن في كروب التخزين بنجاح.")
        except Exception as e:
            print(f"❌ خطأ أثناء ترقية البوت: {e}")

def format_yt_caption(video, page, total=10):
    title = video.get('title', 'بدون عنوان')
    url = video.get('url', '')
    desc = video.get('description', 'لا يوجد وصف متاح.')
    desc = desc[:100] + "..." if desc else "لا يوجد وصف."
    duration = video.get('duration_string', 'غير معروف')
    views = video.get('view_count', 0)
    views_formatted = f"{views:,}" if views else "غير معروف"
    channel = video.get('channel', 'قناة غير معروفة')
    channel_url = video.get('channel_url', '')

    return (
        f"🎥 **[{title}]({url})**\n\n"
        f"📝 **الوصف:** {desc}\n"
        f"⏱ **المدة:** {duration} | 👁 **المشاهدات:** {views_formatted}\n"
        f"👤 **القناة:** [{channel}]({channel_url})\n\n"
        f"📄 **النتيجة:** {page}/{total}"
    )

def get_pagination_buttons(video_id, current_page, total_pages=10):
    return [
        [
            Button.inline("السابق ⬅️", data=f"yt_prev_{current_page}"),
            Button.inline(f"{current_page}/{total_pages}", data="yt_ignore"),
            Button.inline("التالي ➡️", data=f"yt_next_{current_page}")
        ],
        [Button.inline("القائمة 🗂", data=f"yt_menu_{current_page}")],
        [
            Button.inline("تحميل صوت 🎵", data=f"yt_dla_{video_id}"),
            Button.inline("تحميل فيديو 🎬", data=f"yt_dlv_{video_id}")
        ]
    ]

def get_menu_buttons(total_pages=10):
    buttons, row = [], []
    for i in range(1, total_pages + 1):
        row.append(Button.inline(str(i), data=f"yt_jump_{i}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([Button.inline("الرجوع 🔙", data="yt_jump_1")])
    return buttons

# ==========================================
# Handlers (يتم استدعاؤها أو ربطها بعميل السورس)
# ==========================================

async def user_search_handler(event):
    """(User Client) التقاط أمر .بحث"""
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.edit("⚠️ يرجى كتابة اسم المقطع بعد الأمر.")

    YT_CHAT_CACHE[event.sender_id] = event.chat_id

    await event.edit("🔍 جاري البحث ...")
    try:
        inline_results = await event.client.inline_query(Config.BOT_USERNAME, f"yts {query}")
        if inline_results:
            await inline_results[0].click(event.chat_id)
            await event.delete()
        else:
            await event.edit("❌ لم يتم العثور على نتائج.")
    except Exception as e:
        await event.edit(f"❌ خطأ الانلاين: {str(e)}")


async def bot_inline_handler(event):
    """(Assistant Client) استقبال الانلاين وإرجاع النتائج"""
    query = event.pattern_match.group(1).strip()
    user_id = event.sender_id
    
    # 1. جلب النتائج من المحرك الصاروخي
    results = yt_fast_search(query)
    if not results: return
    
    # 2. تخزينها في الرام للتقليب السريع
    YT_SEARCH_CACHE[user_id] = results
    
    first_video = results[0]
    caption = format_yt_caption(first_video, page=1, total=len(results))
    buttons = get_pagination_buttons(first_video['id'], current_page=1, total_pages=len(results))
    thumb_url = first_video.get('thumbnails', [{}])[-1].get('url', 'https://via.placeholder.com/1280x720.png?text=No+Thumb')

    result = event.builder.photo(
        file=thumb_url,
        title=first_video.get('title', 'نتيجة يوتيوب'),
        text=caption,
        buttons=buttons
    )
    await event.answer([result], cache_time=0)


async def bot_callback_handler(event):
    """(Assistant Client) التعامل مع الأزرار"""
    data = event.data.decode('utf-8').split('_')
    action = data[1] 
    user_id = event.sender_id

    if action == "ignore":
        return await event.answer("📄 لعرض رقم الصفحة فقط.")

    if user_id not in YT_SEARCH_CACHE:
        return await event.answer("⚠️ انتهت الجلسة. ابحث من جديد.", alert=True)
    
    results = YT_SEARCH_CACHE[user_id]
    total_pages = len(results)

    # --- القائمة ---
    if action == "menu":
        try:
            await event.edit(buttons=get_menu_buttons(total_pages))
        except MessageNotModifiedError: pass
        return

    # --- التقليب ---
    if action in ["prev", "next", "jump"]:
        current_page = int(data[2])
        if action == "prev": new_page = current_page - 1 if current_page > 1 else total_pages
        elif action == "next": new_page = current_page + 1 if current_page < total_pages else 1
        else: new_page = current_page 
            
        video = results[new_page - 1]
        caption = format_yt_caption(video, page=new_page, total=total_pages)
        buttons = get_pagination_buttons(video['id'], current_page=new_page, total_pages=total_pages)
        thumb_url = video.get('thumbnails', [{}])[-1].get('url')
        
        try:
            await event.edit(text=caption, file=thumb_url, buttons=buttons)
        except MessageNotModifiedError: pass
        return


    if action in ["dla", "dlv"]:
        video_id = data[2]
        dl_type = "a" if action == "dla" else "v"
        type_str = "الصوت 🎵" if dl_type == "a" else "الفيديو 🎬"
        
        await event.answer(f"⏳ جاري معالجة {type_str}...", alert=False)
        await event.edit(buttons=[[Button.inline("⏳ جاري التحميل من يوتيوب...", data="yt_ignore")]])
        
        file_path, file_size_mb = await yt_secure_download(video_id, dl_type=dl_type)
        
        if not file_path:
            return await event.edit("❌ فشل التحميل بسبب قيود يوتيوب.", buttons=get_pagination_buttons(video_id, current_page, total_pages))

        await event.edit(buttons=[[Button.inline("🚀 جاري الرفع إلى تيليجرام...", data="yt_ignore")]])
        
        caption = f"download done {'🎶' if dl_type == 'a' else '🎬'}\n@{Config.BOT_USERNAME}"
        
        target_chat = YT_CHAT_CACHE.get(user_id, user_id) 

        try:
            
            
            if file_size_mb < 50:
                await event.client.send_file(target_chat, file_path, caption=caption)
            else:
                await luxur_client.send_file(target_chat, file_path, caption=caption)
            
            await event.edit(buttons=get_pagination_buttons(video_id, current_page, total_pages))
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except Exception as e:
            print(f"Upload Error: {e}")
            await event.edit(buttons=[[Button.inline("❌ فشل الرفع", data="yt_ignore")]])




@luxur.ar_cmd(events.NewMessage(outgoing=True, pattern=r'^\.بحث (.*)'))
async def wrap_user_search(event):
    await user_search_handler(event)

@luxur.tgbot.on(events.InlineQuery(pattern=r'^yts (.*)'))
async def wrap_inline(event):
    await bot_inline_handler(event)

@luxur.tgbot.on(events.CallbackQuery(pattern=b'^yt_(.*)'))
async def wrap_callback(event):
    await bot_callback_handler(event)