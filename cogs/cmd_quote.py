import discord, re
from discord.ext import commands
from botfunctions import userdb, checks
import traceback, sys

# This cog is for the !quote command.
# Mods are able to add quotes to the list.
# Users are able to have the bot cite random
# quotes that have previously been added.

class QuoteCmdCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quote', aliases=['quotes'])
    async def _quote(self, ctx, *args):
        # First we'll see if the user has entered a number
        # i.e. a message ID.
        got_id = False
        if len(args) >= 1 and args[0].isdigit():
            message_id = args[0]
            got_id = True

        # For ease of use there are a number of aliases for each command.
        add_commands    = ('add', 'ajouter', 'ajoute', 'ajoutez', 'ajoutons', 'adda')
        name_commands   = ('name', 'shortcut', 'alias')
        remove_commands = ('remove', 'delete', 'erase', 'del', 'rmv', 'undo')
        random_commands = ('random', 'rnd', 'any', 'whatever', 'anything')
        read_commands   = ('read', 'cite', 'lookup', 'number', 'name', 'by', 'from')
        help_commands   = ('help', 'how', 'howto')

        # Let's make sure the database exists.
        userdb.create()

        # Below are the different functions which will execute once
        # we've figured out the desired command.

        ####################
        ### ADD QUOTE
        ####################
        async def add_quote(id):
            # We need to find the post with the correct ID to add it.
            msg = False
            for channel in ctx.guild.text_channels:
                try:
                    msg = await channel.get_message(id)
                except:
                    pass # this means the id wasn't in that channel

            if msg != False:
                new_quote = userdb.crt_quote(ctx, msg)
                if new_quote != None:
                    await ctx.send(embed=new_quote)
                else:
                    await ctx.send('%s That quote is already in the database.' % (ctx.author.mention,))
            else:
                await ctx.send('%s I wasn\'t able to find any post with the id: %s' % (ctx.author.mention, str(id)))

        ####################
        ### NAME QUOTE
        ####################
        async def name_quote(id, name):
            found, updated, old_name = userdb.name_quote(id, name)

            if found and updated:
                # Alternative 1:
                # All went smoothly.
                if old_name != None and old_name != str():
                    await ctx.send('%s The shortcut was changed from **%s** to **%s**!' % (ctx.author.mention, str(old_name), name))
                else:
                    await ctx.send('%s The shortcut **%s** was assigned to the requested quote.' % (ctx.author.mention, name))

            elif found and not updated:
                # Alternative 2:
                # Found but couldn't update.
                if old_name == name:
                    await ctx.send('%s That quote already has the shortcut **%s**!' % (ctx.author.mention, name))
                else:
                    await ctx.send('%s I found the quote, but for some reason I wasn\'t able to update the name/shortcut.' % (ctx.author.mention,))

            elif not found:
                # Alternative 3:
                # The quote wasn't found.
                await ctx.send('%s I can\'t find that quote and thus can\'t assign a name/shortcut to it!' % (ctx.author.mention,))

        ####################
        ### REMOVE/DELETE QUOTE
        ####################
        async def delete_quote(id):
            id = str(id)
            quote = userdb.delete_quote(id)

            # If quote is a tuple it means error.
            # If it's not it means it's an embed.
            if isinstance(quote, tuple):
                found, multiple = quote
                if found and multiple:
                    await ctx.send('%s I found multiple matches with that name/id, so I didn\'t delete anything. My bad, this shouldn\'t happen...' % (ctx.author.mention,))

                elif not found:
                    await ctx.send('%s Your search didn\'t return any matches, so I haven\'t deleted anything.' % (ctx.author.mention,))

            else:
                await ctx.send(('%s Success! The following quote was deleted:' % (ctx.author.mention,)), embed=quote)

        ####################
        ### RANDOM QUOTE
        ####################
        async def random_quote(id):
            id = str(id)
            if id != None:
                quote = userdb.get_quote_rnd(id)
            else:
                quote = userdb.get_quote_rnd(None)

            # Found quote!
            if (quote != None):
                await ctx.send(embed=quote)

            # Found no quote with chosen ID.
            elif (quote == None) and (id != None):
                await ctx.send('%s I couldn\'t find any quotes by the mentioned user.' % (ctx.author.mention,))

            # Found no quotes in the database.
            elif (quote == None) and (id == None):
                await ctx.send('%s There doesn\'t seem to be any quotes in the database. Perhaps consider adding one?' % (ctx.author.mention,))

        ####################
        ### READ QUOTE
        ####################
        async def read_quote(id):
            id = str(id)
            quote = userdb.get_quote_id(id)
            if quote != None:
                await ctx.send(embed=quote)
            else:
                await ctx.send('%s Sorry I couldn\'t find any quote by the name/id **%s**!' % (ctx.author.mention, id))

        ####################
        ### COUNT QUOTES
        ####################
        async def count_quotes(id):
            pass


        # tested:
        # await add_quote(479269483219910668) # quote by mrfreeze
        # await add_quote(479755040509263882) # quote by mrfreeze
        # await add_quote(479971404503318539) # quote by terminal
        # await name_quote(479269483219910668, 'test3')
        # await read_quote('479269483219910668')
        # await random_quote(None)
        # await random_quote('154516898434908160') # with terminal user ID.
        # await random_quote(471904058270154754) # with mrfreeze user id
        # await delete_quote(479269483219910668) # deleting quote with unique name/id.
        # await delete_quote(479755040509263882) # stopped deleting due to multiple matches



def setup(bot):
    bot.add_cog(QuoteCmdCog(bot))
