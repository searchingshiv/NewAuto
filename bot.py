import logging
import logging.config
import asyncio
import os
import requests
from aiohttp import web
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from apscheduler.schedulers.background import BackgroundScheduler
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, PORT
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script

import pytz
from datetime import date, datetime 

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        logging.info(script.LOGO)
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))

        # Start web server to handle webhook
        app = web.Application()
        app.router.add_get("/alive", self.alive)
        app.router.add_post(f"/{BOT_TOKEN}", self.handle_update)

        runner = web.AppRunner(app)
        await runner.setup()
        bind_address = "0.0.0.0"
        site = web.TCPSite(runner, bind_address, PORT)
        await site.start()

        logging.info(f"Webhook server started on {bind_address}:{PORT}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def handle_update(self, request):
        update = await request.json()
        if update:
            self.process_new_updates([types.Update.de_json(update)])
        return web.Response(text="OK")

    async def alive(self, request):
        return web.Response(text="I am alive!")

# ===============[ FIX RENDER PORT ISSUE ]================ #

RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
if RENDER_EXTERNAL_URL:
    logging.info(f"Render URL detected: {RENDER_EXTERNAL_URL}")
else:
    logging.warning("Render URL not detected. Using default localhost URL.")

def ping_self():
    url = f"{RENDER_EXTERNAL_URL}/alive"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Ping successful!")
        else:
            logging.error(f"Ping failed with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Ping failed with exception: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_job(ping_self, 'interval', minutes=3)
    scheduler.start()

# Start bot
start_scheduler()
app = Bot()
app.run()
