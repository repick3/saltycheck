# These are the dependecies. The bot depends on these to function, hence the name. Please do not change these unless your adding to them, because they can break the bot.
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform

import saltycheck
import nightbot
import settings

# Here you can modify the bot's prefix and description and wether it sends help in direct messages or not.
client = Bot(description="repick's rebot", command_prefix="$", pm_help = False)

# This is what happens everytime the bot launches. In this case, it prints information like server count, user count the bot is connected to, and the bot id in the console.
# Do not mess with it because the bot can break, if you wish to do so, please consult me or someone trusted.
@client.event
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('Support Discord Server: https://discord.gg/FNNNgqb')
    print('Github Link: https://github.com/Habchy/BasicBot')
    print('--------')
    print('You are running BasicBot v2.1') #Do not change this. This will really help us support you, if you need support.
    print('Created by Habchy#1665')
    for server in client.servers:
        for channel in server.channels:
            print(channel, channel.id)

    # return await client.change_presence(game=discord.Game(name='PLAYING No Salt')) #This is buggy, let us know if it doesn't work.
    # return await client.change_presence() #This is buggy, let us know if it doesn't work.
    return client

# This is a basic example of a call and response command. You tell it do "this" and it does it.
@client.command()
async def ping(*args):
    '''Say that to my face fucker and not online and see what happens'''

    await client.say(":galaxybrain:")
# After you have modified the code, feel free to delete the line above so it does not keep popping up everytime you initiate the ping commmand.
    

@client.command()
async def check(*args):
    '''Get the current saltybet status'''

    salty_mode = await saltycheck.get_mode()
    await client.say(salty_mode)


@client.command()
async def salt(*args):
    '''Say a saltybet nightbot command.'''
    try:
        nightbot_text =  nightbot.commands[args[0]]
    except:
        nightbot_text = "Try again gamer"
    await client.say(nightbot_text)

# @client.command()
# async def kill(*args):
#     exit()


client.loop.create_task(saltycheck.salty_checker(client))
client.run(settings.DISCORD_CLIENT_TOKEN)

# Basic Bot was created by Habchy#1665
# Please join this Discord server if you need help: https://discord.gg/FNNNgqb
# Please modify the parts of the code where it asks you to. Example: The Prefix or The Bot Token
# This is by no means a full bot, it's more of a starter to show you what the python language can do in Discord.
# Thank you for using this and don't forget to star my repo on GitHub! [Repo Link: https://github.com/Habchy/BasicBot]

# The help command is currently set to be not be Direct Messaged.
# If you would like to change that, change "pm_help = False" to "pm_help = True" on line 9.