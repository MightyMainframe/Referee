import discord
import requests
import json



def run(client, message, *args):
    with open('config.json') as f:
        configjson = json.load(f)

    with open('whitelist.json') as f:
        whitelistjson = json.load(f)
    if len(args) < 1:
        response = requests.get(
            "https://api.mojang.com/users/profiles/minecraft/{nickname}".format(
            nickname=message.author.display_name))
    elif len(args) == 1:
        response = requests.get(
            "https://api.mojang.com/users/profiles/minecraft/{nickname}".format(
            nickname=args[1]))
    else:
        return client.send_message(client.channel, "Too many arguments")
    if response.status_code == 204:
        return client.send_message(message.channel,
        "Couldn't add {user} to the whitelist. {A}{B}".format(
            user=message.author.mention,
            A="Make sure your Nickname on this server matches your minecraft",
            B=" in-game-name."))
    else:
        role = discord.utils.get(message.server.roles,
            id=configjson["RoleToAssign"])
        whitelist_data = response.json()
        whitelistjson.append(whitelist_data)
        with open('whitelist.json', 'w') as f:
            json.dump(whitelistjson, f)
        actions = [client.add_roles(message.author, role), client.send_message(
            message.channel, "{user}{A}".format(user=message.author.mention,
            A=" is added to the UHC!"))]
        return actions
