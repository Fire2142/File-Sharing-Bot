from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import sys
import time
import json
import requests
from datetime import datetime, timedelta

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT, SHORTENER_API, SHORTENER_URL

ascii_art = """
 _   .-')    _  .-')               ('-. .-.               .-')    .-') _    
( '.( OO )_ ( \( -O )             ( OO )  /              ( OO ). (  OO) )   
 ,--.   ,--.),------.   ,----.    ,--. ,--. .-'),-----. (_)---\_)/     '._  
 |   `.'   | |   /`. ' '  .-./-') |  | |  |( OO'  .-.  '/    _ | |'--...__) 
 |         | |  /  | | |  |_( O- )|   .|  |/   |  | |  |\  \:` `. '--.  .--' 
 |  |'.'|  | |  |_.' | |  | .--, \|       |\_) |  |\|  | '..`''.)   |  |    
 |  |   |  | |  .  '.'(|  | '. (_/|  .-.  |  \ |  | |  |.-._)   \   |  |    
 |  |   |  | |  |\  \  |  '--'  | |  | |  |   `'  '-'  '\       /   |  |    
 `--'   `--' `--' '--'  `------'  `--' `--'     `-----'  `-----'    `--'    
"""

# Dictionary to store verification timestamps
verified_users = {}

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Force Subscription Check
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                sys.exit()

        # Verify Database Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning("Make sure bot is admin in DB Channel!")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/YourChannel")
        print(ascii_art)
        print("Welcome to File Sharing Bot")

        # Web-server
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

# Shortener Verification
async def verify_user(client, message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in verified_users:
        last_verified_time = verified_users[user_id]
        if current_time - last_verified_time < 21600:  # 6 hours
            await message.reply("✅ You are already verified!")
            return True

    short_url = f"{SHORTENER_URL}?api={SHORTENER_API}&url=https://t.me/{client.username}?start=verify"
    await message.reply(f"🔗 Please verify by clicking this link:\n\n{short_url}\n\nAfter verification, click /start.")
    return False

# Command to start bot
@Client.on_message(filters.command("start"))
async def start(client, message):
    if await verify_user(client, message):
        await message.reply("Welcome! You can now access the stored files.")

# Intercepting file access
@Client.on_message(filters.text & filters.private)
async def file_access(client, message):
    if await verify_user(client, message):
        await message.reply("Here is your requested file!")

if __name__ == "__main__":
    Bot().run()
 
