import discord
import json

def run(client, message, roles, *args):
    with open('whitelist.json') as f:
        whitelistjson = json.load(f)
    whitelist_send = "Here is the whitelist: ```{}```".format(whitelistjson)
    if not args:
        if roles[0] in message.author.roles or roles[1] in message.author.roles:
            if len(whitelist_send) <= 2000:
                return client.send_message(message.channel, whitelist_send)
            else:
                return client.send_file(
                    message.channel,
                    "whitelist.json",
                    content="Here's the whitelist!")
        else:
            return client.send_message(message.channel, "Invalid permissions")
    else:
        if args[0].lower() == "clear":
            whitelistjson = []
            with open('whitelist.json', 'w') as f:
                json.dump(whitelistjson, f)
            return client.send_message(message.channel, "Whitelist cleared!")
        elif args[0].lower() == "file":
            return client.send_file(
                message.channel,
                "whitelist.json",
                content="Here's the whitelist!")
        elif args[0].lower() == "get":
            if roles[0] in message.author.roles or roles[1] in message.author.roles:
                if len(whitelist_send) <= 2000:
                    return client.send_message(message.channel, whitelist_send)
                else:
                    return client.send_file(
                        message.channel,
                        "whitelist.json",
                        content="Here's the whitelist!")
            else:
                return client.send_message(message.channel,
                    "Invalid permissions")
