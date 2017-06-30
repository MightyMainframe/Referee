import discord

async def run(client, message, roles, *args):
    await client.send_message(message.channel, "Test Confirmed:tm:")
