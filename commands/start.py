import discord

def run(client, message, roles, *args):
    response = [ client.change_presence(
        game=discord.Game(
        name='a UHC! Come join!')),
    client.send_message(message.channel, "Status changed! Let's get roling!")]
    return response
