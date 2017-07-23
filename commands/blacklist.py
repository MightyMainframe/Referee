import json_handler
from datetime import date



"""Random Variable Assignments"""
blacklist_types = {
"user":"users",
"users":"users",
"account":"users",
"channel":"channels",
"channels":"channels",
"thread":"channels"
}



async def run(client, message, command, *args):
    database = json_handler.load("config")
    user_roles = []
    for role in message.author.roles:
        user_roles.append(role.name)
    if database["modRole"] in user_roles or database["adminRole"] in user_roles:
        if len(args) >= 2:
            function = args[0].lower()
            blacklist = args[1].lower()
            ID = args[2].strip("<@>")
            reason = ""
            if len(args) > 3:
                reason = " ".join(args[3:])
            if blacklist in blacklist_types:
                if function == "add":
                        #Checks to make sure it is safe to add/remove from blacklist
                        await blacklist_check(client, message, function,
                                              blacklist, ID, reason)
                elif function == "remove":
                        #Checks to make sure it is safe to add/remove from blacklist
                        await blacklist_check(client, message, function,
                                              blacklist, ID, reason)
                else:
                    #Error - Invalid subcommand
                    await client.send_message(message.channel, "Invalid Subcommand")
            else:
                #Error - Invalid blacklist.
                await client.send_message(message.channel,
                                          "Invalid blacklist alias.")
        else:
            #Error - Not enough arguments
            await client.send_message(message.channel,
                                      "Not enough arguments.")
    else:
        await client.send_message(message.channel,
                                  "Invalid permissions.")



async def blacklist_check(client, message, function, blacklist, ID, reason):
    database = json_handler.load("config")
    #Checks to see if the ID is in the corresponding blacklist
    if function == "add":
        for unit in database["blacklist"][blacklist_types[blacklist]]:
            if unit["id"] == ID:
                #Error - ID already in specified blacklist
                await client.send_message(message.channel,
                                          "Already in specified blacklist.")
                return
        #Adds to blacklist after checking
        await modify_blacklist(client, message, function,
                                   blacklist, ID, reason)
    elif function == "remove":
        for unit in database["blacklist"][blacklist_types[blacklist]]:
            if unit["id"] == ID:
                #Removes from blacklist
                await modify_blacklist(client, message, function,
                                       blacklist, ID, reason)
                return
        #Error - ID not in specified blacklist
        await client.send_message(message.channel,
                                  "Not in specified blacklist.")



async def modify_blacklist(client, message, function, blacklist, ID, reason):
    database = json_handler.load("config")
    if function == "add":
        #Adds ID to the specified blacklist
        database["blacklist"][blacklist_types[blacklist]].append({"id":ID,
                                        "reason":reason,
                                        "added_by":str(message.author),
                                        "date of":date.today().isoformat()})
        json_handler.write("config", database)
        await client.send_message(message.channel,
            "`{}` has been added to the {} blacklist with reason: `{}`".format(
                                                ID,
                                                blacklist_types[blacklist],
                                                reason))
    elif function == "remove":
        #Removes ID from the specified blacklist
        for entry in database["blacklist"][blacklist_types[blacklist]]:
            if entry["id"] == ID:
                database["blacklist"][blacklist_types[blacklist]].remove(entry)
        json_handler.write("config", database)
        await client.send_message(message.channel,
                            "`{}` has been removed from the {} blacklist".format(
                                        ID, blacklist_types[blacklist]))
