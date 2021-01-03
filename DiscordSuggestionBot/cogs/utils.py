import discord
from discord.ext import commands
import time
from datetime import datetime

#Global vars
suggestionChannelID = 0
logginChannelID = 0
suggestions = []

class suggestionRecord():
    def __init__(self, u_ID, m_ID):
        self.u_ID = u_ID
        self.m_ID = m_ID

class utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Creates embed to send to user
    def embedMsg(self, message):
        embed = discord.Embed(
        title = "Suggestion bot ❓",
        description = message,
        colour = discord.Colour.purple()
        )
        return embed

    def loopUsers(self, reaction):
        for user in suggestions:
        #Check messages are the same
            if reaction.message.id == user.m_ID.id:
                #Gets user info
                suggestionAuthor = self.client.get_user(user.u_ID)
                return suggestionAuthor

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='your suggestions'))

    @commands.command()
    async def setup (self, ctx):
        if ctx.message.author.guild_permissions.administrator:
            global suggestionChannelID, logginChannelID
            if ctx.message.author.id != self.client.user.id:
                def is_correct(self):
                    return ctx.message.author == ctx.message.author 
                #Getting channel for suggestions
                await ctx.send("> Enter the channel for suggestion creation")
                suggestionChannel = await self.client.wait_for('message', check=is_correct, timeout = 30)
                suggestionChannel = suggestionChannel.content
                #Getting channel ID for suggestions
                for channel in ctx.guild.channels:
                    if channel.name == suggestionChannel:
                        suggestionChannelID = channel.id
                #Getting channel for logging 
                await ctx.send("> Enter the channel for suggestion logging")
                loggingChannel = await self.client.wait_for('message', check=is_correct, timeout = 30)
                loggingChannel = loggingChannel.content
                #Getting channel ID for loggin 
                for channel in ctx.guild.channels:
                    if channel.name == loggingChannel:
                        logginChannelID = channel.id
                #Getting user info
                channel = self.client.get_channel(suggestionChannelID)
                #Sending the message
                await channel.send(embed=self.embedMsg("Send your suggestion here for us to review."))

    @commands.Cog.listener()
    async def on_message(self, message):
        global suggestionChannelID, suggestionAuthorID, logginChannelID
        #Getting time
        now = datetime.now()
        #Formatting time
        timeMsgSent = now.strftime("%d/%m/%Y | %H:%M")
        suggestion = ""
        if message.channel.id == suggestionChannelID:
            if message.author.id != self.client.user.id:
                #Getting message history
                suggestionAuthorID = message.author.id
                channel = self.client.get_channel(message.channel)
                suggestionHistory = await message.channel.history(limit=1).flatten()
                for s in suggestionHistory:
                    suggestion = s.content
                await message.delete()
                #Creating a message and adding history into an embed
                embed=discord.Embed(title = "Suggestion bot ❓", description = suggestion, color = discord.Colour.purple())
                embed.set_footer(text = f"Suggested by {message.author} | {timeMsgSent}", icon_url=message.author.avatar_url)
                channel = self.client.get_channel(logginChannelID)
                #Sending embeded message to logging channel
                suggestionMSG = await channel.send(embed=embed)
                #Storing authorID and messageID to class and then adding object to a array
                _suggestionRecord = suggestionRecord(suggestionAuthorID, suggestionMSG)
                suggestions.append(_suggestionRecord)
                #Reacting to message
                await suggestionMSG.add_reaction('✅')
                await suggestionMSG.add_reaction('📌')
                await suggestionMSG.add_reaction('❌')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global suggestionAuthorID, suggestions, logginChannelID
        channel = reaction.message.channel
        if channel.id == logginChannelID:
            if user.id != self.client.user.id:
                if reaction.emoji == '✅':
                    await self.loopUsers(reaction).send(embed=self.embedMsg("We will be implementing this into our server."))
                    #Clears reactions
                    await reaction.message.clear_reactions()
                if reaction.emoji == '📌':
                    await self.loopUsers(reaction).send(embed=self.embedMsg("We are busy right now. We will respond as soon as possible."))
                    #Pins the message to chat
                    await reaction.message.pin()
                    channel = self.client.get_channel(logginChannelID)
                    await channel.purge(limit=1)
                if reaction.emoji == '❌':
                    await self.loopUsers(reaction).send(embed=self.embedMsg("We don't think this suits our server but thank you for the suggestion."))
                    await reaction.message.clear_reactions()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        global logginChannelID
        channel = payload.channel_id
        if channel == logginChannelID:
            if payload.user_id != self.client.user.id:
                channel = self.client.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                await message.unpin()

                

                    
def setup(client):
    client.add_cog(utils(client))
