import discord

def run(client, message, roles, *args):
    await client.change_presence(
        game=discord.Game(name='a UHC!'))
    await client.send_message(message.channel,
                              "Let's get to the dieing already!")
