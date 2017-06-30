import json_handler
import discord

alert = "{}, your role has been removed"


async def run(client, message, command, *args):
    config = json_handler.load("config")
    role = discord.utils.get(message.server.roles, id=config["RoleToAssign"])
    await client.remove_roles(message.author, role)
    await client.send_message(message.channel,alert.format(message.author.name))