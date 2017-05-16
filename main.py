#-------------------------------------------------------------------------#
#     "#" signs at the beginning of lines are comments these lines do not #
#     affect how to code is read by Python, I would highly reccomend to   #
#     comment the potato out of the code so it is as easy to read as      #
#          possible, (it doesn't need to be as formatted as mine)         #
#-------------------------------------------------------------------------#
import discord
import json
import requests

client = discord.Client()

# Set a game status
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='UHC organization'))

@client.event
async def on_message(message):
    with open('teams.json') as f:
        teams = json.load(f)

    with open('config.json') as f:
        configjson = json.load(f)

    with open('whitelist.json') as f:
        whitelistjson = json.load(f)
    
    _modRole = discord.utils.get(message.server.roles, name=configjson["modRole"])
    _adminRole = discord.utils.get(message.server.roles, name=configjson["adminRole"])
#               Message Prefix ----v
    if message.content.startswith('!'):
        command, *args = message.content[1:].split()
        cmd = command.lower()
#       !test command
        if cmd == "test":
            await client.send_message(message.channel, "Yup things seem to working... for now")
#       !join command
        elif cmd == "join":
            response = requests.get("https://api.mojang.com/users/profiles/minecraft/{nickname}".format(nickname=message.author.display_name))
            if response.status_code == 204:
                await client.send_message(message.channel, "Couldn't add {user} to the whitelist. Make sure your Nickname on this server matches your minecraft IGN.".format(user=message.author.mention))
            else:
                await client.send_message(message.channel, "{user} is added to the UHC!".format(user=message.author.mention))
                role = discord.utils.get(message.server.roles, id=configjson["RoleToAssign"])
                whitelist_data = response.json()
                whitelistjson.append(whitelist_data)
                with open('whitelist.json', 'w') as f:
                    json.dump(whitelistjson, f)
                await client.add_roles(message.author, role)
#       !setRole command
        elif cmd == "setrole":
            if _modRole in message.author.roles or _adminRole in message.author.roles:
                completeID = args[0]
                _roleToAssign = completeID.strip('<>&@')
                role_dict = {"RoleToAssign": _roleToAssign}
                configjson.update(role_dict)
                with open('config.json', 'w') as f:
                    json.dump(configjson, f)
                await client.send_message(message.channel, "{user} | Changed default `!join` role to {role}!".format(user=message.author.mention, role=discord.utils.get(message.server.roles, id=_roleToAssign).mention))
            else:
                await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
#       !setTeam command, takes 2 args, teamName and a mention to the teamRole
        elif cmd == "setteam":
            if _modRole in message.author.roles or _adminRole in message.author.roles:
                teamName = args[0]
                teamID = args[1].strip('<>&@')
                team_dict = {teamName: teamID}
                teams.update(team_dict)
                with open('teams.json', 'w') as f:
                    json.dump(teams, f)
                teamRole = discord.utils.get(message.server.roles, id=teamID)
                await client.send_message(message.channel, "Team {teamName} was added with role {team}".format(teamName=teamName, team=teamRole.mention))
            else:
                await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
#       !team command to join team, takes 1 arg, teamName
        elif cmd == "team":
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
                    await client.send_message(message.channel, "{user} You're already in a team! You can't join two!".format(user=message.author.mention))
                else:
                    await client.send_message(message.channel, "{user} joined team {team}".format(user=message.author.mention, team=teamName))
                    role = discord.utils.get(message.server.roles, id=teams[teamName])
                    await client.add_roles(message.author, role)
            else:
                await client.send_message(message.channel, "This team is non existing! Please contact a Moderator or Administrator if you think this team should exist.")
        elif cmd == "start":
            await client.change_presence(game=discord.Game(name='A UHC! Come join!'))
            await client.send_message(message.channel, "Status changed! Let's get roling!")
        elif cmd == "whitelist":
            if not args:
                if _modRole in message.author.roles or _adminRole in message.author.roles:
                    await client.send_message(message.channel, "Here is the whitelist: ```{}```".format(whitelistjson))
                else:
                    await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")
            else:
                if args[0].lower() == "clear":
                    whitelistjson = []
                    with open('whitelist.json', 'w') as f:
                        json.dump(whitelistjson, f)
                    await client.send_message(message.channel, "Whitelist cleared!")
                elif args[0].lower() == "get":
                    if _modRole in message.author.roles or _adminRole in message.author.roles:
                        await client.send_message(message.channel, "Here is the whitelist: ```{}```".format(whitelistjson))
                    else:
                        await client.send_message(message.channel, "You don't have the permissions needed to use this command! If this is a mistake please contact a Moderator or Administrator")







#    DO NOT LEAVE THE TOKEN IN HERE FROM NOW ON
#    (Bad things could happen if it is public)
client.run('TOKEN')
