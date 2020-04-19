import discord
from discord.ext import commands
from loguru import logger

from cogs.utils.database import sql_execute


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !rr create "[title]" [emote1] [role1] [emote2] [role2] ...
    # Creates a reaction role menu with multiple emote-role pairs
    @commands.has_permissions(manage_roles=True)
    @commands.command(name='rrcreate')
    async def rrcreate(self, ctx, title, *args):
        embed = discord.Embed(title=title, color=discord.Color.blue())
        emotes, roles = args[::2], args[1::2]
        for emote, role in zip(emotes, roles):
            embed.add_field(name=emote, value=role, inline=False)
        message = await ctx.send(embed=embed)

        for emote in emotes:
            await message.add_reaction(emote)

        sql = 'INSERT INTO reactions(message_id, channel_id, emote_name, role_name) VALUES '
        vals = []
        for emote, role in zip(emotes, roles):
            sql += '(?, ?, ?, ?),'
            vals.extend([(message.id), (ctx.channel.id), (emote.replace(':', '')), (role)])
        sql = sql[:-1]
        sql_execute(sql, vals)

        await ctx.send(embed=discord.Embed(title=f'Your message ID is: {message.id}', color=discord.Color.green()))


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
