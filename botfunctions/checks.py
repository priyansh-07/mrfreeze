# Here we define all of our custom checks.
import discord

async def is_owner(ctx):
    # @commands.check(checks.is_owner)
    if ctx.author.id != 154516898434908160:
        await ctx.send(ctx.author.mention + ' You\'re not the boss of me, only Terminal is allowed to issue that command.')
    return ctx.author.id == 154516898434908160

async def is_mod(ctx):
    # @commands.check(checks.is_mod)
    # This check can also be used as a command with a member object,
    # depending on the input, output may vary.

    if isinstance(ctx, discord.member.Member):
        mod_status = (discord.utils.get(ctx.guild.roles, name='Administration') in ctx.roles)

    elif isinstance(ctx, discord.ext.commands.context.Context):
        mod_status = (discord.utils.get(ctx.guild.roles, name='Administration') in ctx.author.roles)
        if not mod_status:
            await ctx.send(ctx.author.mention + ' Only mods are allowed to use that command.')

    return mod_status
