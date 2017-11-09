import json_handler

async def run(client, message, roles, *args):
    config = json_handler.load("config")
    user_roles = []
    for role in message.author.roles:
        user_roles.append(role.name)
    if config["modRole"] in user_roles or config["adminRole"] in user_roles:
        completeID = args[0]
        roleToAssign = completeID.strip('<>&@')
        role_dict = {"RoleToAssign": roleToAssign}
        configjson.update(role_dict)
        config = json_handler.load("config")
        await client.send_message(message.channel,
                      "{user} | Changed default `!join` role to {role}!".format(
                      user=message.author.mention,
                      role=discord.utils.get(message.server.roles,
                            id=roleToAssign).mention))
    else:
        await client.send_message(message.channel, "Invalid permissions.")
