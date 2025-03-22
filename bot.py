#(©)MrGhostsx

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT


ascii_art = """
 _   .-')    _  .-')               ('-. .-.               .-')    .-') _    
( '.( OO )_ ( \( -O )             ( OO )  /              ( OO ). (  OO) )   
 ,--.   ,--.),------.   ,----.    ,--. ,--. .-'),-----. (_)---\_)/     '._  
 |   .'   | |   /. ' '  .-./-') |  | |  |( OO'  .-.  '/    _ | |'--...__) 
 |         | |  /  | | |  |_( O- )|   .|  |/   |  | |  |\  \: . '--.  .--' 
 |  |'.'|  | |  |_.' | |  | .--, \|       |\_) |  |\|  | '..''.)   |  |    
 |  |   |  | |  .  '.'(|  | '. (_/|  .-.  |  \ |  | |  |.-._)   \   |  |    
 |  |   |  | |  |\  \  |  '--'  | |  | |  |   '  '-'  '\       /   |  |    
 --'   --' --' '--'  ------'  --' --'     -----'  -----'    `--'    
"""

class Bot(Client):
    def init(self):
        super().init(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(name).warning(a)
                self.LOGGER(name).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(name).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(name).info("\nBot Stopped. Join https://t.me/Tech_Shreyansh for support")
                sys.exit()
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(name).warning(e)
            self.LOGGER(name).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(name).info("\nBot Stopped. Join https://t.me/Tech_Shreyansh for support")
            sys.exit()
     
# Shortener Verification Function
async def verify_user(client, message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in verified_users:
        last_verified_time = verified_users[user_id]
        if current_time - last_verified_time < 21600:  # 6 hours
            return True  # User is already verified

    # Generate Shortener Link for Verification
    short_url = f"{SHORTENER_URL}?api={SHORTENER_API}&url=https://t.me/{client.username}?start=verify"
    await message.reply(f"🔗 Please verify by clicking this link:\n\n{short_url}\n\nAfter verification, click /start.")
    return False

# Command to start bot
@Client.on_message(filters.command("start"))
async def start(client, message):
    if await verify_user(client, message):
        await message.reply("✅ Verification Successful! You can now access the stored files.")
        self.set_parse_mode(ParseMode.HTML)
     # File Access with Verification
@Client.on_message(filters.private & ~filters.command("start"))
async def file_access(client, message):
    if await verify_user(client, message):
        await message.reply("📂 Here is your requested file!")
    else:
        await message.reply("⚠️ Please verify your account using the shortener link first.")
     
        self.LOGGER(name).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/Tech_Shreyansh29")
        print(ascii_art)
        print("""Welcome to MrGhostsx File Sharing Bot""")
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(name).info("Bot stopped.")
