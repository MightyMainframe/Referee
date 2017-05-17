import discord
import json

def run(client, message, roles, *args):
    with open('config.json') as f:
        configjson = json.load(f)
    with open('teams.json') as f:
        teams = json.load(f)
    if roles[0] in message.author.roles or roles[1] in message.author.roles:
        teamName = args[0]
        teamID = args[1].strip('<>&@')
        team_dict = {teamName: teamID}
        teams.update(team_dict)
        with open('teams.json', 'w') as f:
            json.dump(teams, f)
        teamRole = discord.utils.get(message.server.roles, id=teamID)
        return client.send_message(message.channel,
            "Team {teamName} was added with role {team}".format(
            teamName=teamName,
            team=teamRole.mention))
    else:
        return client.send_message(message.channel, "Invalid permissions.")
