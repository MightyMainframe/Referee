import discord
import json_handler

async def run(client, message, command, *args):
    config = json_handler.load("config")
    teams = json_handler.load("teams")
    user_roles = []
    for role in message.author.roles:
        user_roles.append(role.name)
    if config["modRole"] in user_roles or config["adminRole"] in user_roles:
        teamName = args[0]
        teamID = args[1].strip('<>&@')
        teams[teamName] = teamID
        json_handler.write("teams", teams)
        teamRole = discord.utils.get(message.server.roles, id=teamID)
        await client.send_message(message.channel,
                            "Team {teamName} was added with role {team}".format(
                                teamName=teamName,
                                team=teamRole.mention))
    else:
        await client.send_message(message.channel, "Invalid permissions.")
