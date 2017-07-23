import json_handler
import discord

alert = "{}, your role has been removed"


async def run(client, message, command, *args):
    config = json_handler.load("config")
    whitelist = json_handler.load("whitelist")
    if not len(args):
        for whitelisted in whitelist:
            if whitelisted["name"] == message.author.display_name:
                whitelist.remove(whitelisted)
    else:
        for whitelisted in whitelist:
            if whitelisted["name"] == args[0]:
                whitelist.remove(whitelisted)
    json_handler.write("whitelist", whitelist)
    role = discord.utils.get(message.server.roles, id=config["RoleToAssign"])
    await client.remove_roles(message.author, role)
    await client.send_message(message.channel,alert.format(message.author.name))