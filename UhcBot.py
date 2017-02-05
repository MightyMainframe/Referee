#-------------------------------------------------------------------------#
#     "#" signs at the beginning of lines are comments these lines do not #
#     affect how to code is read by Python, I would highly reccomend to   #
#     comment the potato out of the code so it is as easy to read as      #
#          possible, (it doesn't need to be as formatted as mine)         #
#-------------------------------------------------------------------------#
import discord

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
            await client.send_message(message.channel, "{user} You have been added".format(user=message.author.mention))
            for role in message.server.roles:
                if role.name == "Bot-tester":
                    roleToAssign = role
            await client.add_roles(message.author, roleToAssign)

#    DO NOT LEAVE THE TOKEN IN HERE FROM NOW ON
#    (Bad things could happen if it is public)
client.run('TOKEN')
