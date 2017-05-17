import discord
import json

def run(client, message, roles, *args):
    with open('teams.json') as f:
        teams = json.load(f)
    with open('teams.json') as f:
        teams = json.load(f)
    teamName = args[0].lower()
    if teamName in teams:
        allRoles = []
        userRoles = []
        for team in teams:
            allRoles.append(teams[team])
        allRolesSet = set(allRoles)
        for role in message.author.roles:
            userRoles.append(role.id)
        userRolesSet = set(userRoles)
        if allRolesSet.intersection(userRolesSet):
            return client.send_message(message.channel,
                "{user} You're already in a team! You can't join two!".format(
                    user=message.author.mention))
        else:
            role = discord.utils.get(message.server.roles, id=teams[teamName])
            response = [client.send_message(message.channel,
                "{user} joined team {team}".format(
                user=message.author.mention,
                team=teamName)),
            client.add_roles(message.author, role)]
            return response
    else:
        return client.send_message(message.channel,
        """This team is non existant!
Please contact a Moderator or Administrator if you think this in an error""")
