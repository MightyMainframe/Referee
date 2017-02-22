#-------------------------------------------------------------------------#
#     "#" signs at the beginning of lines are comments these lines do not #
#     affect how to code is read by Python, I would highly reccomend to   #
#     comment the potato out of the code so it is as easy to read as      #
#          possible, (it doesn't need to be as formatted as mine)         #
#-------------------------------------------------------------------------#
import discord
import json

client = discord.Client()

with open('teams.json') as f:
    teams = json.load(f)

with open('config.json') as f:
    configjson = json.load(f)

# Set a game status
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='Some UHC\'s'))

@client.event
async def on_message(message):
#               Message Prefix ----v
    if message.content.startswith('!'):
        command, *args = message.content[1:].split()
#       !test command
        if command == "test":
            await client.send_message(message.channel, "Yup things seem to working... for now")
#       !join command
        elif command == "join":
            await client.send_message(message.channel, "{user} is added to the UHC!".format(user=message.author.mention))
            role = discord.utils.get(message.server.roles, id=configjson["RoleToAssign"])
            await client.add_roles(message.author, role)
#       !setRole command
        elif command == "setRole":
            _modRole = discord.utils.get(message.server.roles, name=configjson["modRole"])
            _adminRole = discord.utils.get(message.server.roles, name=configjson["adminRole"])
            if _modRole in message.author.roles or _adminRole in message.author.roles:
                completeID = args[0]
                _roleToAssign = completeID.strip('<>&@')
                role_dict = {"RoleToAssign": _roleToAssign}
                configjson.update(role_dict)
                with open('config.json', 'w') as f:
                    json.dump(configjson, f)
            else:
                await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
#       !setTeam command, takes 2 args, teamName and a mention to the teamRole
        elif command == "setTeam":
            _modRole = discord.utils.get(message.server.roles, name=configjson["modRole"])
            _adminRole = discord.utils.get(message.server.roles, name=configjson["adminRole"])
            if _modRole in message.author.roles or _adminRole in message.author.roles:
                teamName = args[0]
                teamID = args[1].strip('<>&@')
                team_dict = {teamName: teamID}
                teams.update(team_dict)
                with open('teams.json', 'w') as f:
                    json.dump(teams, f)
                teamRole = discord.utils.get(message.server.roles, id=teamID)
                await client.send_message(message.channel, teamRole.mention)
            else:
                await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
#       !team command to join team, takes 1 arg, teamName
        elif command == "team":
            teamName = args[0]
            if teamName in teams:
                allRoles = []
                for team in teams:
                    allRoles.append(team)
                allRolesSet = set(allRoles)
                userRolesSet = set(message.author.roles)
                if allRolesSet.intersection(userRolesSet):
                    await client.send_message(message.channel, "{user} You're already in a team! You can't join two!".format(user=message.author.mention))
                else:
                    await client.send_message(message.channel, "{user} joined team {team}".format(user=message.author.mention, team=teamName))
                    role = discord.utils.get(message.server.roles, id=teams[teamName])
                    await client.add_roles(message.author, role)
            else:
                await client.send_message(message.channel, "This team is non existing! Please contact a Moderator or Administrator if you think this team should exist.")









#    DO NOT LEAVE THE TOKEN IN HERE FROM NOW ON
#    (Bad things could happen if it is public)
client.run('TOKEN')
