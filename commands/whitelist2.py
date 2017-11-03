import discord
import json_handler

whitelist_message = "Here is the whitelist:\n```json\n{}```"


async def run(client, message, roles, *args):
    config = json_handler.load("config")
    user_roles = []
    for role in message.author.roles:
        user_roles.append(role.name)
    if config["modRole"] in user_roles or config["adminRole"] in user_roles:
        if len(args):
            whitelist = json_handler.load("whitelist2")
            subcommand = args[0].lower()
            if subcommand == "get":
                if len(whitelist_message.format(whitelist)) <= 2000:
                    whitelist_content = str(whitelist)
                    await client.send_message(message.channel,
                          whitelist_message.format(whitelist_content.replace("'","\"")))
                else:
                    await client.send_file(message.channel, 
                                           "whitelist2.json",
                                           content="Here is the whitelist:")
            elif subcommand == "clear":
                whitelist = []
                json_handler.write("whitelist2", whitelist)
                await client.send_message(message.channel, "Whitelist cleared!")
            elif subcommand == "file":
                await client.send_file(message.channel,
                                       "whitelist2.json",
                                       content="Here is the whitelist:")
            else:
                await client.send_message(message.channel,"Invalid subcommand.")
        else:
            await client.send_message(message.channel, "Not enough arguments.")