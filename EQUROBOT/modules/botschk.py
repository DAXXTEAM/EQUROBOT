import asyncio
from pyrogram import filters
from EQUROBOT import app as bot, scr2
from config import OWNER_ID

BOT_LIST = ["EQUROBOT", "YesikooBot"]

@bot.on_message(filters.command("botschk") & filters.user(OWNER_ID))
async def bots_chk(_, message):
    msg = await message.reply_photo(photo="https://telegra.ph/file/4d303296e4fac9a40ea07.jpg", caption="**ᴄʜᴇᴄᴋɪɴɢ ʙᴏᴛs sᴛᴀᴛs ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ...**")
    response = "**ᴄʜᴇᴄᴋɪɴɢ ʙᴏᴛs sᴛᴀᴛs ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ**\n\n"
    for bot_username in BOT_LIST:
        try:
            bot = await scr2.get_users(bot_username)
            bot_id = bot.id
            await asyncio.sleep(0.5)
            bot_info = await scr2.send_message(bot_id, "/start")
            await asyncio.sleep(3)
            async for bot_message in scr2.get_chat_history(bot_id, limit=1):
                if hasattr(bot_message.from_user, 'id') and bot_message.from_user.id == bot_id:
                    response += f"╭⎋ [{bot.first_name}](tg://user?id={bot.id})\n╰⊚ **sᴛᴀᴛᴜs: ᴏɴʟɪɴᴇ ✨**\n\n"
                else:
                    response += f"╭⎋ [{bot.first_name}](tg://user?id={bot.id})\n╰⊚ **sᴛᴀᴛᴜs: ᴏғғʟɪɴᴇ ❄️**\n\n"
        except Exception as e:
            response += f"╭⎋ {bot_username}\n╰⊚ **sᴛᴀᴛᴜs: ᴇʀʀᴏʀ ❌**\n"
    
    await msg.edit_text(response)
    
