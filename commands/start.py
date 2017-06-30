import discord

async def run(client, message, roles, *args):
    user_roles = []
    for role in message.author.roles:
        user_roles.append(role.name)
    if config["modRole"] in user_roles or config["adminRole"] in user_roles:
        await client.change_presence(game=discord.Game(name='a UHC!'))
        await client.send_message(message.channel,
                                  "Let's get to the dieing already!")
