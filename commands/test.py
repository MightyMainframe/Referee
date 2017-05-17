
import discord

def run(client, message, roles, *args):
    return client.send_message(message.channel, "Test Confirmed:tm:")
