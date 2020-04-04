import discord
from discord.ext import commands

from cogs.utils.checks import is_bot_owner_check

import git


class Administration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @is_bot_owner_check()
    @commands.command(name='gitpull')
    async def git_pull(self, ctx):
        git_dir = "./"
        try:
            g = git.cmd.Git(git_dir)
            g.pull()
            embed = discord.Embed(title=":white_check_mark: Successfully pulled from repository", color=0x00df00)
            await ctx.channel.send(embed=embed)

        except Exception as e:
            errno, strerror = e.args
            embed = discord.Embed(title="Command Error!",
                                  description=f"Git Pull Error: {errno} - {strerror}",
                                  color=0xff0007)
            await ctx.channel.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.command(name='kick')
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(self.gen_msg('kicked', member, reason))

    @commands.has_permissions(ban_members=True)
    @commands.command(name='ban')
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(self.gen_msg('banned', member, reason))

    @commands.has_permissions(ban_members=True)
    @commands.command(name='unban')
    async def unban(self, ctx, *, member):
        banned_list = await ctx.guild.bans()
        member_name, member_id = member, None
        if '#' in member:
            member_name, member_id = member.split('#')

        found = False

        for ban_entry in banned_list:
            user = ban_entry.user
            if user.name == member_name and member_id == user.discriminator or member_id == None:
                await ctx.guild.unban(ban_entry.user)
                await ctx.send(f'{user.mention} has been unbanned.')
                found = True
                break
        
        if not found:
            await ctx.send(f'Could not find {member}.')

    @commands.has_permissions(ban_members=True)
    @commands.command(name='tempban')
    async def tempban(self, ctx, member : discord.Member, *, reason=None):
        await ctx.send(self.gen_msg('banned', member, reason))

    @is_bot_owner_check()
    @commands.command(name='mute')
    async def mute(self, ctx, member : discord.Member, *, reason=None):
        await ctx.send(self.gen_msg('muted', member, reason))

    @is_bot_owner_check()
    @commands.command(name='tempmute')
    async def tempmute(self, ctx, member : discord.Member, *, reason=None):
        await ctx.send(self.gen_msg('muted', member, reason))

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('Pong! {}')

    def gen_msg(self, verb, member, reason):
        msg = f'{member.mention} was {verb}'
        if reason != None:
            msg += f' for {reason}'
        msg += '!'
        return msg


def setup(bot):
    bot.add_cog(Administration(bot))