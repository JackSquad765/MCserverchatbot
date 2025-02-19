import discord
import asyncio
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Discord Bot Config
TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token
CHANNEL_ID = 123456789012345678  # Replace with your Discord channel ID
LOG_FILE_PATH = "server/logs/latest.log"  # Update to match your server's path

# Discord bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

class LogHandler(FileSystemEventHandler):
    """Watches the Minecraft log file for new messages."""
    def __init__(self):
        self.last_position = 0

    def on_modified(self, event):
        if event.src_path.endswith("latest.log"):
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as file:
                file.seek(self.last_position)
                new_lines = file.readlines()
                self.last_position = file.tell()

                for line in new_lines:
                    if "]: <" in line:  # Detects chat messages
                        msg = line.split("]: <")[1]
                        username, message = msg.split("> ", 1)
                        asyncio.run_coroutine_threadsafe(send_to_discord(username, message), client.loop)

async def send_to_discord(username, message):
    """Sends Minecraft chat messages to Discord."""
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"**{username}**: {message}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    observer = Observer()
    observer.schedule(LogHandler(), path=os.path.dirname(LOG_FILE_PATH), recursive=False)
    observer.start()

client.run(TOKEN)
