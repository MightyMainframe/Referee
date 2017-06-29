import discord
import json_handler

whitelist_message = "Here is the whitelist:```{}```"


async def run(client, message, roles, *args):
    if len(args):
        whitelist = json_handler.load("whitelist")
        subcommand = args[0].lower()
        if subcommand == "get":
            if len(whitelist_message.format(whitelist)) <= 2000:
                await client.send_message(message.channel,
                                          whitelist_message.format(whitelist))
            else:
                await client.send_file(message.channel, 
                                       "whitelist.json",
                                       content="Here is the whitelist:")
        elif subcommand == "clear":
            whitelist = []
            json_handler.write("whitelist", whitelist)
            await client.send_message(message.channel, "Whitelist cleared!")
        elif subcommand == "file":
            await client.send_file(message.channel,
                                   "whitelist.json",
                                   content="Here is the whitelist:")
        else:
            await client.send_message(message.channel, "Invalid subcommand.")
    else:
        await client.send_message(message.channel, "Not enough arguments.")