#-------------------------------------------------------------------------#
#     "#" signs at the beginning of lines are comments these lines do not #
#     affect how to code is read by Python, I would highly reccomend to   #
#     comment the potato out of the code so it is as easy to read as      #
#          possible, (it doesn't need to be as formatted as mine)         #
#-------------------------------------------------------------------------#
import discord
import config

client = discord.Client()

@client.event
async def on_message(message):
#               Message Prefix ----v
    if message.content.startswith('!'):
        command, *args = message.content[1:].split()
#       !test command
        if command == "test":
            await client.send_message(message.channel, "Yup things seem to working... for now")
#       End Command
        elif command == "join":
            await client.send_message(message.channel, "{user} is added to the UHC!".format(user=message.author.mention))
            role = discord.utils.get(message.server.roles, id=config.roleToAssign)
            await client.add_roles(message.author, role)
            await client.delete_message(message)
        elif command == "setRole":
            _modRole = discord.utils.get(message.server.roles, name=config.modRole)
            _adminRole = discord.utils.get(message.server.roles, name=config.adminRole)
            if _modRole in message.author.roles or _adminRole in message.author.roles:
                print(args)
                completeID = args[0]
                _roleToAssign = completeID.strip('<>&@')
                config.roleToAssign = _roleToAssign
                print(config.roleToAssign)
            else:
                await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
        elif command == "setTeam":
            _modRole = discord.utils.get(message.server.roles, name=config.modRole)
            _adminRole = discord.utils.get(message.server.roles, name=config.adminRole)
            if _modRole in message.author.roles or _adminRole in message.author.roles:
                teamName = args[0]
                teamID = args[1].strip('<>&@')
                teamRole = discord.utils.get(message.server.roles, id=teamID)
                await client.send_message(message.channel, teamRole.mention)
            else:
                await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
#    DO NOT LEAVE THE TOKEN IN HERE FROM NOW ON
#    (Bad things could happen if it is public)
client.run('TOKEN')
