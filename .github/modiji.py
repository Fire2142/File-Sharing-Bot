from pyrogram import Client, filters
import requests
import time
from rich.console import Console
from rich.panel import Panel
import config  # Added import for config

console = Console()

# Check if MODIJI_API_KEY exists in config
if not hasattr(config, 'MODIJI_API_KEY'):
    raise Exception("Please add MODIJI_API_KEY to your config.py")

# API endpoint
MODIJI_API_URL = "https://api.modijiurl.com/api"

@Client.on_message(filters.command("short") & filters.user(config.ADMIN_IDS))  
async def short_url_command(client, message):
    """
    Command: /short {url}
    Description: Shortens a URL using ModijiURL API
    """
    try:
        # Extract URL from command
        command = message.text.split()
        if len(command) != 2:
            await message.reply_text(
                "❌ **Invalid command format!**\n\n"
                "**Usage:** `/short url`\n"
                "**Example:** `/short https://example.com`",
                quote=True
            )
            return

        url = command[1]
        
        
        status_msg = await message.reply_text(
            "🔄 **Processing your URL...**",
            quote=True
        )

        # API request parameters
        params = {
            'api': config.MODIJI_API_KEY,  
            'url': url,
            'format': 'json'
        }
        
        
        time.sleep(2)
        
        
        response = requests.get(MODIJI_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'success':
            shortened_url = data.get('shortenedUrl')
            
            await status_msg.edit_text(
                f"✅ **URL Shortened Successfully!**\n\n"
                f"**Original URL:**\n`{url}`\n\n"
                f"**Shortened URL:**\n`{shortened_url}`\n\n"
                f"Powered by @Thealphabotz"
            )
        else:
            await status_msg.edit_text(
                "❌ **Failed to shorten URL!**\n\n"
                "Please check your URL and try again."
            )
            
    except IndexError:
        await message.reply_text(
            "❌ **Please provide a URL to shorten!**\n\n"
            "**Usage:** `/short url`",
            quote=True
        )
    except requests.RequestException as e:
        await status_msg.edit_text(
            f"❌ **API Error:**\n`{str(e)}`\n\n"
            "Please try again later."
        )
    except Exception as e:
        await status_msg.edit_text(
            f"❌ **An unexpected error occurred:**\n`{str(e)}`"
        )
