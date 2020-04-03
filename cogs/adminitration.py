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

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("Pong!")
        await ctx.add_reaction(":ping_pong:")


def setup(bot):
    bot.add_cog(Administration(bot))