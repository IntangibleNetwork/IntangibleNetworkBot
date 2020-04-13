import discord
from discord.ext import commands
from loguru import logger

from cogs.utils.checks import is_bot_owner_check
from cogs.utils.time import get_time_string, get_datetime

import git


class Administration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @is_bot_owner_check()
    @commands.command(name='gitpull')
    async def git_pull(self, ctx):
        git_dir = './'
        try:
            g = git.cmd.Git(git_dir)
            g.pull()
            embed = discord.Embed(title=':white_check_mark: Successfully pulled from repository', color=0x00df00)
            await ctx.channel.send(embed=embed)

        except Exception as error:
            errno, strerror = e.args
            embed = discord.Embed(title='Command Error!',
                                  description=f'Git Pull Error: {errno} - {strerror}',
                                  color=0xff0007)
            await ctx.channel.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.command(name='kick')
    async def kick(self, ctx, member:discord.Member=None, *, reason=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return
        try:
            await member.kick(reason=reason)
            await ctx.send(self.gen_msg('kicked', member, reason=reason))
        except Exception as errorrror:
            await ctx.send(f'Error: {member} could not be kicked.')
            logger.exception(f'Error in the !kick command. [{error}]')

    @commands.has_permissions(ban_members=True)
    @commands.command(name='ban')
    async def ban(self, ctx, member:discord.Member=None, *, reason=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return
        try:
            await member.ban(reason=reason)
            await ctx.send(self.gen_msg('banned', member, reason=reason))
        except Exception as error:
            await ctx.send(f'Error: {member} could not be banned.')
            logger.exception(f'Error in the !ban command. [{error}]')

    @commands.has_permissions(ban_members=True)
    @commands.command(name='unban')
    async def unban(self, ctx, *, member=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return

        member_name, member_id = member, None
        if '#' in member:
            member_name, member_id = member.split('#')

        ban_list = await ctx.guild.bans()
        for ban_entry in ban_list:
            user = ban_entry.user
            if user.name == member_name and member_id == user.discriminator or member_id == None:
                try:
                    await ctx.guild.unban(user)
                    await ctx.send(self.gen_msg('unbanned', user))
                except Exception as error:
                    await ctx.send(f'Error: {member} could not be unbanned.')
                    logger.exception(f'Error in the !unban command. [{error}]')
                return

        await ctx.send(f'Could not find {member}.')
    
    @commands.has_permissions(ban_members=True)
    @commands.command(name='tempban')
    async def tempban(self, ctx, member:discord.Member=None, time=None, *, reason=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return
        if time is None:
            await ctx.send('Please specify a time.')
            return
        try:
            await member.ban(reason=reason)
            await ctx.send(self.gen_msg('banned', member, time, reason))
            self.bot.timer_manager.create_timer('tempban', get_datetime(time), args=(ctx, member))
        except Exception as error:
            await ctx.send(f'Error: Something went wrong.')
            logger.exception(f'Error in the !tempban command. [{error}]')

    @commands.Cog.listener()
    async def on_tempban(self, ctx, member):
        await ctx.guild.unban(member)
        await ctx.send(self.gen_msg('unbanned', member))

    @commands.has_permissions(manage_roles=True)
    @commands.command(name='mute')
    async def mute(self, ctx, member:discord.Member=None, *, reason=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return
        try:
            role = discord.utils.get(ctx.guild.roles, name='Muted')
            if role is None:
                role = await ctx.guild.create_role(name='Muted')
                await ctx.channel.set_permissions(role, send_messages=False)
            await member.add_roles(role)
            await ctx.send(self.gen_msg('muted', member, reason=reason))
        except Exception as error:
            await ctx.send(f'Error: {member} could not be muted.')
            logger.exception(f'Error in the !mute command. [{error}]')

    @commands.has_permissions(manage_roles=True)
    @commands.command(name='unmute')
    async def unmute(self, ctx, member:discord.Member=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return
        try:
            await member.remove_roles(discord.utils.get(ctx.guild.roles, name='Muted'))
            await ctx.send(self.gen_msg('unmuted', member))
        except Exception as error:
            await ctx.send(f'Error: {member} could not be unmuted.')
            logger.exception(f'Error in the !unmute command. [{error}]')

    @commands.has_permissions(manage_roles=True)
    @commands.command(name='tempmute')
    async def tempmute(self, ctx, member:discord.Member=None, time=None, *, reason=None):
        if member is None:
            await ctx.send('Please specify a member.')
            return
        if time is None:
            await ctx.send('Please specify a time.')
            return
        try:
            role = discord.utils.get(ctx.guild.roles, name='Muted')
            if role is None:
                role = await ctx.guild.create_role(name='Muted')
                await ctx.channel.set_permissions(role, send_messages=False)
            await member.add_roles(role)
            await ctx.send(self.gen_msg('muted', member, time, reason))
            self.bot.timer_manager.create_timer('tempmute', get_datetime(time), args=(ctx, member))
        except Exception as error:
            await ctx.send(f'Error: Something went wrong.')
            logger.exception(f'Error in the !tempmute command. [{error}]')

    @commands.Cog.listener()
    async def on_tempmute(self, ctx, member):
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name='Muted'))
        await ctx.send(self.gen_msg('unmuted', member))

    @commands.has_permissions(manage_messages=True)
    @commands.command(name='clear')
    async def clear(self, ctx, amount=20):
        messages = []
        async for message in ctx.message.channel.history(limit=int(amount)):
            messages.append(message)
        await ctx.message.channel.delete_messages(messages)

    def gen_msg(self, verb, member, timer=None, reason=None):
        msg = f'{member.mention} was {verb}'
        if timer is not None:
            msg += f' for {get_time_string(timer)}'
        msg += '!'
        if reason != None:
            msg += f'\nReason: {reason}'
        return msg


def setup(bot):
    bot.add_cog(Administration(bot))