import discord
import json
import os
import psycopg2

import src.commands as commands
from src.collabbot import CollabBot

bot=CollabBot(None,None,None)

config = json.load(open('config.json'))

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

client = discord.Client()


@client.event
async def on_ready():
    global bot
    bot = CollabBot(conn, client, config)
    commands.init(bot)
    print("Bot is ready")
    await client.change_presence(activity=discord.Game(name="$help"))


@client.event
async def on_message(message):
    if message.content.startswith('$'):
        await bot.run_command_on_message(message)

client.run(os.environ['CB_LOGIN'])