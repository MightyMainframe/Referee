import discord
import requests
import json_handler



async def run(client, message, roles, *args):
    config = json_handler.load("config")
    whitelist = json_handler.load("whitelist")
    
    user_roles = []
    for role in message.author.roles:
        user_roles.append(role.name)
    role = discord.utils.get(message.server.roles,
            id=config["RoleToAssign"])
    if role in user_roles:
        await client.send_message(message.channel, "You already joined!")
        return
    
#  Testing for arguments
    if len(args) < 1:
        response = requests.get(
            "https://api.mojang.com/users/profiles/minecraft/{nickname}".format(
            nickname=message.author.display_name))
    elif len(args) == 1:
        response = requests.get(
            "https://api.mojang.com/users/profiles/minecraft/{nickname}".format(
            nickname=args[0]))
    else:
        await client.send_message(message.channel, "Too many arguments")


    if response.status_code == 204:
        if len(args):
            await client.send_message(message.channel,
                "Couldn't add `{user}` to the whitelist. {A}{B}{C}".format(
                user=args[0],
                A="Make sure your Nickname on this server matches your minecraft",
                B=" in-game-name or you add your username after the command like,",
                C=" \"{}join [in-game-name]\" (**CASE SENSITIVE**)".format(
                                                     config["command-prefix"])))
            return
        await client.send_message(message.channel,
           "Couldn't add {user} to the whitelist. {A}{B}{C}".format(
            user=message.author.mention,
            A="Make sure your Nickname on this server matches your minecraft",
            B=" in-game-name or you add your username after the command like,",
            C=" \"{}join [in-game-name]\" (**CASE SENSITIVE**)".format(
                                                 config["command-prefix"])))
    else:
        role = discord.utils.get(message.server.roles,
            id=config["RoleToAssign"])
        whitelist_data = response.json()
        uuid = whitelist_data["id"]
        user_name = whitelist_data["name"]
        user_data = {"uuid":uuid, "name":user_name}
        whitelist.append(user_data)
        json_handler.write("whitelist", whitelist)
        await client.add_roles(message.author, role)
        if len(args):
            await client.send_message(message.channel,
                                      "{user}{A}".format(user=args[0],
                                      A=" has been added to the UHC!"))
            return
        await client.send_message(message.channel,
                                "{user}{A}".format(user=message.author.name,
                                A=" has been added to the UHC!"))
