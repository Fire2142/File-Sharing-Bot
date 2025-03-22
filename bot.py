# (©) MrGhostsx

from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime, timedelta
import asyncio

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT

# Store verified users with expiration time
verified_users = {}

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

        user_id = usr_bot_me.id
        current_time = datetime.now()

        # Check if user is already verified
        if user_id in verified_users:
            expire_time = verified_users[user_id]
            if current_time < expire_time:
                print("User already verified. Skipping verification.")
            else:
                print("Verification expired! Re-verifying user...")
                await self.verify_user(user_id)
        else:
            print("User not verified. Performing verification...")
            await self.verify_user(user_id)

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/Tech_Shreyansh for support")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/Tech_Shreyansh for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/Tech_Shreyansh29")
        print(ascii_art)
        print("Welcome to MrGhostsx File Sharing Bot")

        self.username = usr_bot_me.username

        # Web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    async def verify_user(self, user_id):
        verification_link = "https://your-shortener-link.com/verify"
        print(f"User {user_id} needs to verify. Sending link: {verification_link}")

        # Simulating waiting for user verification (Replace with real API response check)
        await asyncio.sleep(5)  # Wait for verification (simulated)

        # Store verification for 6 hours
        verified_users[user_id] = datetime.now() + timedelta(hours=6)
        print(f"User {user_id} verified successfully! Access granted for 6 hours.")

