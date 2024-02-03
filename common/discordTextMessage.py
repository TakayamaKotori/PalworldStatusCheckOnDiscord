import discord


async def sendMessage(client, message, channelId):
    channel = client.get_channel(channelId)
    return await channel.send(content=message)


async def editEmbed(client, embed, channelId, messageId):
    channel = client.get_channel(channelId)
    sent_message = channel.get_partial_message(messageId)

    return await sent_message.edit(embed=embed)


async def sendFileAndMessage(client, channelId, message, filePath, fileName):
    channel = client.get_channel(channelId)

    file = discord.File(fp=filePath, filename=fileName, spoiler=False)
    return await channel.send(content=message, file=file)
