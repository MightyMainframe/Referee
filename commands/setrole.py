import discord

def run(client, message, roles, *args):
    with open('config.json') as f:
        configjson = json.load(f)
    if roles[0] in message.author.roles or roles[1] in message.author.roles:
        completeID = args[0]
        roleToAssign = completeID.strip('<>&@')
        role_dict = {"RoleToAssign": roleToAssign}
        configjson.update(role_dict)
        with open('config.json', 'w') as f:
            json.dump(configjson, f)
        return client.send_message(message.channel,
            "{user} | Changed default `!join` role to {role}!".format(
            user=message.author.mention,
            role=discord.utils.get(message.server.roles,
                id=roleToAssign).mention))
    else:
        return client.send_message(message.channel, "Invalid permissions.")
