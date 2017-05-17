#-------------------------------------------------------------------------#
#     "#" signs at the beginning of lines are comments these lines do not #
#     affect how to code is read by Python, I would highly reccomend to   #
#     comment the potato out of the code so it is as easy to read as      #
#          possible, (it doesn't need to be as formatted as mine)         #
#-------------------------------------------------------------------------#
import discord
import json
import asyncio


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
"join":join.run,
"setrole":setrole.run,
"setteam":setteam.run,
"start":start.run,
"team":team.run,
"test":test.run,
"whitelist":whitelist.run
}
#-----------------------------------------------#

list_compare = []

client = discord.Client()

# Set a game status
@client.event
async def on_ready():
    print("I'm ALIIIIiiIIVEee!")
    #await client.change_presence(game=discord.Game(name='Sign up now!'))

@client.event
async def on_message(message):
    with open('teams.json') as f:
        teams = json.load(f)
    with open('config.json') as f:
        configjson = json.load(f)
    with open('whitelist.json') as f:
        whitelistjson = json.load(f)

    roles=[discord.utils.get(message.server.roles, name=configjson["modRole"]),
    discord.utils.get(message.server.roles, name=configjson["adminRole"])]
#               Message Prefix ----v
    if message.content.startswith('>'):
        command, *args = message.content[1:].split()
        cmd = command.lower()
        if cmd in commands:
            response = commands[cmd](client, message, roles, *args)
            if type(response) == type(list_compare):
                for action in response:
                    try:
                        await action
                        asyncio.sleep(3)
                    except:
                        print("Action Error")
                        asyncio.sleep(3)
            else:
                try:
                    await response
                except:
                    print("Error")
        else:
            await client.send_message(message.channel, "Invalid command")



#    DO NOT LEAVE THE TOKEN IN HERE
client.run('MzEzNTQzMzk4MjEwNDA0MzUy.C_0uPA.bsChbvoa2xSgN2kk4D1JaO2rxpo')
