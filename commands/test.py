
import discord

def run(client, message, *args):
    return client.send_message(message.channel, "Test Confirmed:tm:")
