import discord
import json_handler

team_error = "This team is non existant! Please contact a Moderator or \
Administrator if you think this in an error"

async def run(client, message, roles, *args):
    teams = json_handler.load("teams")
    teamName = args[0]
    if teamName in teams.keys():
        allRoles = []
        userRoles = []
        for team in teams:
            allRoles.append(teams[team])
        allRoles = set(allRoles)
        for role in message.author.roles:
            userRoles.append(role.id)
        userRoles = set(userRoles)
        if allRoles.intersection(userRoles):
            await client.send_message(message.channel,
                "{user} You're already in a team! You can't join two!".format(
                    user=message.author.mention))
        else:
            role = discord.utils.get(message.server.roles, id=teams[teamName])
            await client.send_message(message.channel,
                                      "{user} joined team {team}".format(
                                            user=message.author.mention,
                                            team=teamName))
            await client.add_roles(message.author, role)
    else:
        await client.send_message(message.channel, team_error)
