import glob
import json
import os
import re
import time
from configparser import ConfigParser

import discord
from discord.ext import commands, timers
from loguru import logger

from cogs.utils.checks import is_bot_owner_check
from cogs.utils.database import sql_execute

# sql_execute('CREATE TABLE reactions (entry_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, message_id int NOT NULL, channel_id int NOT NULL, emote_name char(50) NOT NULL, role_name char(50) NOT NULL)')

auth = ConfigParser()
auth.read('auth.ini')  # All my usernames and passwords for the api

#initiate logger test
if auth.get('discord', 'LOG_FILES') == 1:
    logger.add(f"file_{str(time.strftime('%Y%m%d-%H%M%S'))}.log", rotation="10 MB")

logger.debug("====== Starting Bot ======")
logger.debug("\t Version: 1.0")
logger.debug("\t Author: GiraffeKey#5038")

bot = commands.Bot(command_prefix=auth.get('discord', 'PREFIX'))
bot.timer_manager = timers.TimerManager(bot)

def load_cogs(folder):
    os.chdir(folder)
    files = []
    for file in glob.glob("*.py"):
        file = re.search('^([A-Za-z1-9]{1,})(?:.py)$', file).group(1)
        files.append(file)
    return files


def config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return config



@bot.event
async def on_ready():
    """
    When bot is ready and online it prints that its online
    :return:
    """
    logger.debug("====== Bot is now online! ======")


@bot.command()
@is_bot_owner_check()
async def load(ctx, extension):
    try:
        bot.load_extension('cogs.' + extension)
        logger.debug(f'Loaded {extension}')
        await ctx.send(f'Loaded {extension}')
    except Exception as error:
        logger.exception(f"Extension {extension} could not be loaded. [{error}]")


@bot.command()
@is_bot_owner_check()
async def reload(ctx, extension):
    try:
        bot.unload_extension('cogs.' + extension)
        bot.load_extension('cogs.' + extension)
        logger.debug(f'Reloaded {extension}')
        await ctx.send(f'Reloaded {extension}')
    except Exception as error:
        logger.exception(f"Extension {extension} could not be reloaded. [{error}]")


@bot.command()
@is_bot_owner_check()
async def unload(ctx, extension):
    try:
        bot.unload_extension('cogs.' + extension)
        logger.debug(f'Unloaded {extension}')
        await ctx.send(f'{extension} successfully unloaded')
    except Exception as error:
        logger.exception(f"Extension {extension} could not be unloaded. [{error}]")

# Only works with unicode emotes atm
@bot.event
async def on_reaction_add(reaction, user):
    sql = 'SELECT role_name FROM reactions WHERE message_id=? AND channel_id=? AND emote_name=?'
    vals = [(reaction.message.id), (reaction.message.channel.id), (reaction.emoji)]
    reactions = sql_execute(sql, vals)
    roles = [discord.utils.get(reaction.message.channel.guild.roles, name=x[0]) for x in reactions]
    await user.add_roles(*roles)

@bot.event
async def on_reaction_remove(reaction, user):
    sql = 'SELECT role_name FROM reactions WHERE message_id=? AND channel_id=? AND emote_name=?'
    vals = [(reaction.message.id), (reaction.message.channel.id), (reaction.emoji)]
    reactions = sql_execute(sql, vals)
    roles = [discord.utils.get(reaction.message.channel.guild.roles, name=x[0]) for x in reactions]
    await user.remove_roles(*roles)

if __name__ == "__main__":
    bot.remove_command('help')
    extensions = load_cogs('cogs')
    for extension in extensions:
        try:
            bot.load_extension('cogs.'+extension)
            logger.debug(f'Successfully Started {extension} cog.')
        except Exception as error:
            logger.exception(f"Cog \"{extension}\" could not be loaded. [{error}]")

    bot.run(auth.get('discord', 'TOKEN'))