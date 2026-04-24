#by Hussein For LuxuryUB-LuxuryUB
# Hussein
# يمنع منعاً باتاً تخمط الملف خلي عندك كرامه ولتسرقة
# Added some f. by Reda

import asyncio
import time
from LuxuryUB import luxur
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from telethon.events import NewMessage
import requests
from telethon.tl.functions.users import GetFullUserRequest
from ..Config import Config
import re
from telethon import events
c = requests.session()
bot_username = '@EEObot'
bot_username2 = '@A_MAN9300BOT'
bot_username3 = '@MARKTEBOT'
bot_username4 = '@qweqwe1919bot'
bot_username5 = '@xnsex21bot'
bot_username6 = '@DamKombot'
bot_username8 = '@Bellllen192BOT'
LuxuryUB = ['yes']
ConsoleJoker = Config.T7KM
its_Reham = False
its_hussein = False
its_reda = False
its_joker = False
#اياثارات الحسين
@luxur.on(events.NewMessage(incoming=True))
async def Hussein(event):
    if event.message.message.startswith("تجميع المليار") and str(event.sender_id) in ConsoleJoker:
        await event.reply("**᯽︙سيتم تجميع النقاط من بوت المليار , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username)
        await luxur.send_message(bot_username, '/start')
        await asyncio.sleep(4)
        msg0 = await luxur.get_messages(bot_username, limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(4)
        msg1 = await luxur.get_messages(bot_username, limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            await asyncio.sleep(4)

            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"تم الانتهاء من التجميع")

                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages(bot_username, limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await event.edit(f"تم الانضمام في {chs} قناة")
            except:
                msg2 = await luxur.get_messages(bot_username, limit=1)
                await msg2[0].click(text='التالي')
                chs += 1
                await event.edit(f"القناة رقم {chs}")

        await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
@luxur.on(events.NewMessage(incoming=True))
async def Hussein(event):
    if event.message.message.startswith("ايقاف التجميع") and str(event.sender_id) in ConsoleJoker:
        await luxur.send_message(bot_username, "/start")
        await event.reply("** ᯽︙ تم تعطيل عملية تجميع النقاط بنجاح ✓**")
    
@luxur.on(events.NewMessage(incoming=True))
async def Hussein(event):
    if event.message.message.startswith("تجميع الجوكر") and str(event.sender_id) in ConsoleJoker:
        await event.reply("**᯽︙سيتم تجميع النقاط من بوت الجوكر , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username2)
        await luxur.send_message('@A_MAN9300BOT', '/start')
        await asyncio.sleep(2)
        msg0 = await luxur.get_messages('@A_MAN9300BOT', limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(2)
        msg1 = await luxur.get_messages('@A_MAN9300BOT', limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            await asyncio.sleep(2)

            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                   offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"**لاتوجد قنوات للبوت**")
                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages('@A_MAN9300BOT', limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await luxur.send_message("me", f"تم الاشتراك في {chs} قناة")
            except Exception as er:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**\n{er}")
        await luxur.send_message(event.chat_id, "**تم الانتهاء من التجميع !**")

    #else:
        #await event.edit("يجب الدفع لاستعمال هذا الامر !")
@luxur.on(events.NewMessage(incoming=True))
async def Hussein(event):
    if event.message.message.startswith("تجميع العقاب") and str(event.sender_id) in ConsoleJoker:
        await event.reply("**᯽︙سيتم تجميع النقاط من بوت العقاب , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username3)
        await luxur.send_message('@MARKTEBOT', '/start')
        await asyncio.sleep(3)
        msg0 = await luxur.get_messages('@MARKTEBOT', limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(3)
        msg1 = await luxur.get_messages('@MARKTEBOT', limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            await asyncio.sleep(3)
            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                   offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"**لاتوجد قنوات للبوت**")
                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages('@MARKTEBOT', limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await luxur.send_message("me", f"تم الاشتراك في {chs} قناة")
            except:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**")
        await luxur.send_message(event.chat_id, "**تم الانتهاء من التجميع !**")

    #else:
        #await event.edit("يجب الدفع لاستعمال هذا الامر !")
@luxur.on(events.NewMessage(incoming=True))
async def Hussein(event):
    if event.message.message.startswith("تجميع المليون") and str(event.sender_id) in ConsoleJoker:
        await event.reply("**᯽︙سيتم تجميع النقاط من بوت المليون , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username4)
        await luxur.send_message('@qweqwe1919bot', '/start')
        await asyncio.sleep(2)
        msg0 = await luxur.get_messages('@qweqwe1919bot', limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(2)
        msg1 = await luxur.get_messages('@qweqwe1919bot', limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            await asyncio.sleep(2)

            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                   offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"**لاتوجد قنوات للبوت**")
                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages('@qweqwe1919bot', limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await luxur.send_message("me", f"تم الاشتراك في {chs} قناة")
            except:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**")
        await luxur.send_message(event.chat_id, "**تم الانتهاء من التجميع !**")

   # else:
     #   await event.edit("يجب الدفع لاستعمال هذا الامر !")

@luxur.on(admin_cmd(pattern="(تجميع المليار|تجميع مليار)"))
async def _(event):
    await event.edit("**᯽︙سيتم تجميع النقاط من بوت المليار , قبل كل شي تأكد من انك قمت بالانضمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
    channel_entity = await luxur.get_entity(bot_username)
    await luxur.send_message(bot_username, '/start')
    await asyncio.sleep(4)
    msg0 = await luxur.get_messages(bot_username, limit=1)
    await msg0[0].click(2)
    await asyncio.sleep(4)
    msg1 = await luxur.get_messages(bot_username, limit=1)
    await msg1[0].click(0)

    chs = 1
    for i in range(100):
        await asyncio.sleep(4)

        list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        msgs = list.messages[0]
        if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم بتجميع النقاط بطريقة مختلفة') != -1:
            await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
            break

        url = msgs.reply_markup.rows[0].buttons[0].url

        try:
            try:
                await luxur(JoinChannelRequest(url))
            except:
                bott = url.split('/')[-1]
                await luxur(ImportChatInviteRequest(bott))
            msg2 = await luxur.get_messages(bot_username, limit=1)
            await msg2[0].click(text='تحقق')
            chs += 1
            await event.edit(f"تم الانضمام في {chs} قناة")
        except:
            msg2 = await luxur.get_messages(bot_username, limit=1)
            await msg2[0].click(text='التالي')
            chs += 1
            await event.edit(f"القناة رقم {chs}")

    await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
        
@luxur.on(admin_cmd(pattern="(ايقاف التجميع|ايقاف تجميع)"))
async def cancel_collection(event):
    await luxur.send_message('@EEObot', '/start')
    await event.edit("** ᯽︙ تم الغاء التجميع من بوت المليار **")
    
@luxur.on(admin_cmd(pattern="(تجميع الجوكر|تجميع جوكر)"))
async def _(event):
    if LuxuryUB[0] == "yes":
        await event.edit("**᯽︙سيتم تجميع النقاط من بوت الجوكر , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username2)
        await luxur.send_message('@A_MAN9300BOT', '/start')
        await asyncio.sleep(2)
        msg0 = await luxur.get_messages('@A_MAN9300BOT', limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(2)
        msg1 = await luxur.get_messages('@A_MAN9300BOT', limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            if LuxuryUB[0] == 'no':
                break
            await asyncio.sleep(2)

            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                   offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"**لاتوجد قنوات للبوت**")
                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages('@A_MAN9300BOT', limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await luxur.send_message("me", f"تم الاشتراك في {chs} قناة")
            except Exception as er:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**\n{er}")
        await luxur.send_message(event.chat_id, "**تم الانتهاء من التجميع !**")

  #  else:
    #    await event.edit("يجب الدفع لاستعمال هذا الامر !")
@luxur.on(admin_cmd(pattern="(تجميع العقاب|تجميع عقاب)"))
async def _(event):
    if LuxuryUB[0] == "yes":
        await event.edit("**᯽︙سيتم تجميع النقاط من بوت العقاب , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username3)
        await luxur.send_message('@MARKTEBOT', '/start')
        await asyncio.sleep(3)
        msg0 = await luxur.get_messages('@MARKTEBOT', limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(3)
        msg1 = await luxur.get_messages('@MARKTEBOT', limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            if LuxuryUB[0] == 'no':
                break
            await asyncio.sleep(3)

            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                   offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"**لاتوجد قنوات للبوت**")
                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages('@MARKTEBOT', limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await luxur.send_message("me", f"تم الاشتراك في {chs} قناة")
            except:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**")
        await luxur.send_message(event.chat_id, "**تم الانتهاء من التجميع !**")

 #   else:
   #     await event.edit("يجب الدفع لاستعمال هذا الامر !")
@luxur.on(admin_cmd(pattern="(تجميع المليون|تجميع مليون)"))
async def _(event):
    if LuxuryUB[0] == "yes":
        await event.edit("**᯽︙سيتم تجميع النقاط من بوت المليون , قبل كل شي تأكد من انك قمت بلانظمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
        channel_entity = await luxur.get_entity(bot_username4)
        await luxur.send_message('@qweqwe1919bot', '/start')
        await asyncio.sleep(2)
        msg0 = await luxur.get_messages('@qweqwe1919bot', limit=1)
        await msg0[0].click(2)
        await asyncio.sleep(2)
        msg1 = await luxur.get_messages('@qweqwe1919bot', limit=1)
        await msg1[0].click(0)

        chs = 1
        for i in range(100):
            if LuxuryUB[0] == 'no':
                break
            await asyncio.sleep(2)

            list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1,
                                                   offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
            msgs = list.messages[0]
            if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم يتجميع النقاط بطريقه مختلفه') != -1:
                await luxur.send_message(event.chat_id, f"**لاتوجد قنوات للبوت**")
                break
            url = msgs.reply_markup.rows[0].buttons[0].url
            try:
                try:
                    await luxur(JoinChannelRequest(url))
                except:
                    bott = url.split('/')[-1]
                    await luxur(ImportChatInviteRequest(bott))
                msg2 = await luxur.get_messages('@qweqwe1919bot', limit=1)
                await msg2[0].click(text='تحقق')
                chs += 1
                await luxur.send_message("me", f"تم الاشتراك في {chs} قناة")
            except:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**")
        await luxur.send_message(event.chat_id, "**تم الانتهاء من التجميع !**")

#    else:
  #      await event.edit("يجب الدفع لاستعمال هذا الامر !")
@luxur.on(admin_cmd(pattern="(تجميع العرب|تجميع عرب)"))
async def _(event):
    await event.edit("**᯽︙سيتم تجميع النقاط من بوت العرب , قبل كل شي تأكد من انك قمت بالانضمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
    channel_entity = await luxur.get_entity(bot_username5)
    await luxur.send_message(bot_username5, '/start')
    await asyncio.sleep(4)
    msg0 = await luxur.get_messages(bot_username5, limit=1)
    await msg0[0].click(2)
    await asyncio.sleep(4)
    msg1 = await luxur.get_messages(bot_username5, limit=1)
    await msg1[0].click(0)

    chs = 1
    for i in range(100):
        await asyncio.sleep(4)
        list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        msgs = list.messages[0]
        if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم بتجميع النقاط بطريقة مختلفة') != -1:
            await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
            break

        url = msgs.reply_markup.rows[0].buttons[0].url

        try:
            try:
                await luxur(JoinChannelRequest(url))
            except:
                bott = url.split('/')[-1]
                await luxur(ImportChatInviteRequest(bott))
            msg2 = await luxur.get_messages(bot_username5, limit=1)
            await msg2[0].click(text='تحقق')
            chs += 1
            await event.edit(f"تم الانضمام في {chs} قناة")
        except:
            msg2 = await luxur.get_messages(bot_username5, limit=1)
            await msg2[0].click(text='التالي')
            chs += 1
            await event.edit(f"القناة رقم {chs}")

    await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
@luxur.on(admin_cmd(pattern="تجميع دعمكم"))
async def _(event):
    await event.edit("**᯽︙سيتم تجميع النقاط من بوت دعمكم , قبل كل شي تأكد من انك قمت بالانضمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
    channel_entity = await luxur.get_entity(bot_username6)
    await luxur.send_message('@DamKombot', '/start')
    await asyncio.sleep(4)
    msg0 = await luxur.get_messages(bot_username6, limit=1)
    await msg0[0].click(1)
    await asyncio.sleep(4)
    msg1 = await luxur.get_messages(bot_username6, limit=1)
    await msg1[0].click(0)
    chs = 1
    for i in range(100):
        await asyncio.sleep(4)
        list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        msgs = list.messages[0]
        if msgs.message.find('لا يوجد قنوات حالياً 🤍') != -1:
            await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
            break
        msg_text = msgs.message  # الكود تمت كتابتهُ من قبل سورس الجوكر 
        if "اشترك فالقناة @" in msg_text:
            luxury_channel = msg_text.split('@')[1].split()[0]
            try:
                entity = await luxur.get_entity(luxury_channel)
                if entity:
                    await luxur(JoinChannelRequest(entity.id))
                    await asyncio.sleep(4)
                    msg2 = await luxur.get_messages(bot_username6, limit=1)
                    await msg2[0].click(text='اشتركت ✅')
                    chs += 1
                    await event.edit(f"تم الانظمام الى القناة رقم {chs}")
            except:
                await luxur.send_message(event.chat_id, f"**خطأ , ممكن تبندت**")
                break

    await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")

@luxur.on(admin_cmd(pattern="(تجميع عراق|تجميع العراق)"))
async def _(event):
    await event.edit("**᯽︙سيتم تجميع النقاط من بوت العراق , قبل كل شي تأكد من انك قمت بالانضمام الى القنوات الاشتراك الاجباري للبوت لعدم حدوث اخطاء**")
    channel_entity = await luxur.get_entity(bot_username8)
    await luxur.send_message(bot_username8, '/start')
    await asyncio.sleep(4)
    msg0 = await luxur.get_messages(bot_username8, limit=1)
    await msg0[0].click(2)
    await asyncio.sleep(4)
    msg1 = await luxur.get_messages(bot_username8, limit=1)
    await msg1[0].click(0)

    chs = 1
    for i in range(100):
        await asyncio.sleep(4)

        list = await luxur(GetHistoryRequest(peer=channel_entity, limit=1, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        msgs = list.messages[0]
        if msgs.message.find('لا يوجد قنوات في الوقت الحالي , قم بتجميع النقاط بطريقة مختلفة') != -1:
            await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
            break

        url = msgs.reply_markup.rows[0].buttons[0].url

        try:
            try:
                await luxur(JoinChannelRequest(url))
            except:
                bott = url.split('/')[-1]
                await luxur(ImportChatInviteRequest(bott))
            msg2 = await luxur.get_messages(bot_username8, limit=1)
            await msg2[0].click(text='تحقق')
            chs += 1
            await event.edit(f"تم الانضمام في {chs} قناة")
        except:
            msg2 = await luxur.get_messages(bot_username8, limit=1)
            await msg2[0].click(text='التالي')
            chs += 1
            await event.edit(f"القناة رقم {chs}")

    await luxur.send_message(event.chat_id, "تم الانتهاء من التجميع")
    


async def resume_w3d_tasks():
    await asyncio.sleep(10)
    
    if gvarstatus(None, "RATIB_W3D_STATUS") == "true":
        chat_id = int(gvarstatus(None, "RATIB_W3D_CHAT"))
        asyncio.create_task(send_ratib_loop(chat_id))
        
    if gvarstatus(None, "BAKH_W3D_STATUS") == "true":
        chat_id = int(gvarstatus(None, "BAKH_W3D_CHAT"))
        asyncio.create_task(send_bakh_loop(chat_id))

    if gvarstatus(None, "ZRF_W3D_STATUS") == "true":
        chat_id = int(gvarstatus(None, "ZRF_W3D_CHAT"))
        target = gvarstatus(None, "ZRF_W3D_TARGET")
        asyncio.create_task(send_zrf_loop(chat_id, target))

    if gvarstatus(None, "INVEST_W3D_STATUS") == "true":
        chat_id = int(gvarstatus(None, "INVEST_W3D_CHAT"))
        asyncio.create_task(w3d_investment_loop(chat_id))

asyncio.create_task(resume_w3d_tasks())


async def send_ratib_loop(chat_id):
    while gvarstatus(None, "RATIB_W3D_STATUS") == "true":
        try:
            await luxur.send_message(chat_id, 'راتب')
        except: break
        await asyncio.sleep(660)

@luxur.ar_cmd(pattern="راتب وعد$")
async def start_ratib(event):
    if not event.is_group:
        return await event.edit("**هذا الأمر يمكن استخدامه فقط في المجموعات!**")
    if gvarstatus(None, "RATIB_W3D_STATUS") == "true":
        return await event.edit("**راتب وعد مفعل بالفعل.**")
    
    addgvar(None, "RATIB_W3D_STATUS", "true")
    addgvar(None, "RATIB_W3D_CHAT", str(event.chat_id))
    await event.delete()
    asyncio.create_task(send_ratib_loop(event.chat_id))

@luxur.ar_cmd(pattern="ايقاف راتب وعد$")
async def stop_ratib(event):
    delgvar(None, "RATIB_W3D_STATUS")
    delgvar(None, "RATIB_W3D_CHAT")
    await event.edit("**تم تعطيل راتب وعد بنجاح ✅**")


async def send_bakh_loop(chat_id):
    while gvarstatus(None, "BAKH_W3D_STATUS") == "true":
        try:
            await luxur.send_message(chat_id, 'بخشيش')
        except: break
        await asyncio.sleep(660)

@luxur.ar_cmd(pattern="بخشيش وعد$")
async def start_bakh(event):
    if not event.is_group:
        return await event.edit("**هذا الأمر يمكن استخدامه فقط في المجموعات!**")
    if gvarstatus(None, "BAKH_W3D_STATUS") == "true":
        return await event.edit("**بخشيش وعد مفعل بالفعل.**")
    
    addgvar(None, "BAKH_W3D_STATUS", "true")
    addgvar(None, "BAKH_W3D_CHAT", str(event.chat_id))
    await event.delete()
    asyncio.create_task(send_bakh_loop(event.chat_id))

@luxur.ar_cmd(pattern="ايقاف بخشيش وعد$")
async def stop_bakh(event):
    delgvar(None, "BAKH_W3D_STATUS")
    delgvar(None, "BAKH_W3D_CHAT")
    await event.edit("**᯽︙ تم تعطيل بخشيش وعد بنجاح ✓ **")

async def send_zrf_loop(chat_id, target):
    while gvarstatus(None, "ZRF_W3D_STATUS") == "true":
        try:
            await luxur.send_message(chat_id, f"زرف {target}")
        except: break
        await asyncio.sleep(660)

@luxur.ar_cmd(pattern="سرقة وعد(?:\s|$)([\s\S]*)")
async def start_zrf(event):
    if not event.is_group:
        return await event.edit("**هذا الأمر يمكن استخدامه فقط في المجموعات!**")
        
    target = event.pattern_match.group(1).strip()
    if not target:
        return await event.edit("**يرجى كتابة ايدي الشخص مع الامر!**")
        
    if gvarstatus(None, "ZRF_W3D_STATUS") == "true":
        return await event.edit("**عملية السرقة مفعلة بالفعل، قم بايقافها أولاً لتغيير الهدف.**")
    
    addgvar(None, "ZRF_W3D_STATUS", "true")
    addgvar(None, "ZRF_W3D_CHAT", str(event.chat_id))
    addgvar(None, "ZRF_W3D_TARGET", target) # نحفظ الهدف حتى ما ينساه السورس
    await event.delete()
    asyncio.create_task(send_zrf_loop(event.chat_id, target))

@luxur.ar_cmd(pattern="ايقاف سرقة وعد$")
async def stop_zrf(event):
    delgvar(None, "ZRF_W3D_STATUS")
    delgvar(None, "ZRF_W3D_CHAT")
    delgvar(None, "ZRF_W3D_TARGET")
    await event.edit("** ᯽︙ تم ايقاف السرقة بنجاح ✓ **")

async def w3d_investment_loop(chat_id):
    while gvarstatus(None, "INVEST_W3D_STATUS") == "true":
        try:
            await luxur.send_message(chat_id, "فلوسي")
            await asyncio.sleep(3)
            messages = await luxur.get_messages(chat_id, limit=1)
            if messages:
                msg_text = messages[0].message
                parts = msg_text.split()
                # استخراج الرقم لضمان عدم حدوث خطأ
                luxur_amount = next((s for s in parts if s.isdigit()), "0")
                
                if int(luxur_amount) > 500000000:
                    await luxur.send_message(chat_id, f"استثمار {luxur_amount}")
                    await asyncio.sleep(5)
                    joker_msgs = await luxur.get_messages(chat_id, limit=1)
                    await joker_msgs[0].click(text="اي ✅")
                else:
                    await luxur.send_message(chat_id, f"استثمار {luxur_amount}")
        except: break
        await asyncio.sleep(1220)

@luxur.ar_cmd(pattern="استثمار وعد$")
async def start_invest(event):
    if not event.is_group:
        return await event.edit("** ᯽︙ امر الاستثمار يمكنك استعماله في المجموعات فقط 🖤**")
    
    if gvarstatus(None, "INVEST_W3D_STATUS") == "true":
        return await event.edit("**الاستثمار مفعل بالفعل.**")
        
    addgvar(None, "INVEST_W3D_STATUS", "true")
    addgvar(None, "INVEST_W3D_CHAT", str(event.chat_id))
    await event.delete()
    asyncio.create_task(w3d_investment_loop(event.chat_id))

@luxur.ar_cmd(pattern="ايقاف استثمار وعد$")
async def stop_invest(event):
    delgvar(None, "INVEST_W3D_STATUS")
    delgvar(None, "INVEST_W3D_CHAT")
    await event.edit("**تم تعطيل عملية الاستثمار وعد.**")

