#-------------------------------------------------------------------------#
#     "#" signs at the beginning of lines are comments these lines do not #
#     affect how to code is read by Python, I would highly reccomend to   #
#     comment the potato out of the code so it is as easy to read as      #
#          possible, (it doesn't need to be as formatted as mine)         #
#-------------------------------------------------------------------------#
import discord
import asyncio
import json_handler

#-------------- COMMAND IMPORTING --------------#
import commands.test as test
import commands.join as join
import commands.setrole as setrole
import commands.setteam as setteam
import commands.team as team
import commands.start as start
import commands.whitelist as whitelist
#-----------------------------------------------#

#------- Add commands to the parser here -------#
commands = {
"test":test.run,
"whitelist":whitelist.run
}
#-----------------------------------------------#


client = discord.Client()

# Set a game status
@client.event
async def on_ready():
    print("I'm ALIIIIiiIIVEee!")
    #await client.change_presence(game=discord.Game(name='Sign up now!'))

@client.event
async def on_message(message):
    config = json_handler.load("config")
    if message.content.startswith(config["command-prefix"]):
        if message.author.id not in config["blacklist"]["users"].keys():
            if message.channel.id not in config["blacklist"]["channels"].keys():
                command, *args = message.content[1:].split()
                command = command.lower()
                if command in commands:
                    await commands[command](client, message, command, *args)
                else:
                    await client.send_message(message.channel,
                                              "Invalid command.")




#    DO NOT LEAVE THE TOKEN IN HERE
try:
    client.run("TOKEN")
except:
    print("Oh no, it seems as though something went wrong upon login!")