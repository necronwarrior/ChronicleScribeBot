# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Existing classes that we can run through
ACCEPTED_CLASSES = ["Ariane", "Linza", "Morvran", "Neutral", "Ozan", "Raptor", "Vanescula"]

# Setup the required perms: member access and message reading/sending
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/scribe', intents=intents)

def findCardImage(name, path):
    """
    Returns the location of a file from the given name, after recursively looking from path
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[0].lower() == name.lower():
                return os.path.join(root, name)
        for dir in dirs:
            foundName = findCardImage(name, dir)
            if foundName != None:
                return foundName

@bot.event
async def on_ready():
    """
    Pings us botname and connected guild for keeping track of the program from the command line
    """
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

####
#
# Because we accept "/scribe <cardname>" we have to manually check the next arg to see if the user wants another
# command, or fallback to card if they want the shorthand
#
####

PIPE_HELP_TEXT = f"If you type \".scribe <card name>\", I will seek out an image of " \
                 f"the card if I can find it.\n"
@bot.command(name='pipe', aliases=['', ' '])
async def pipe(ctx, *args):
    """
    Takes in the first argument of " " and goes straight to card searching if there are no other protected arguments
    next
    """
    if len(args) == 0:
        await ctx.author.send(f"I require the name of a card, {ctx.author.name}.")
        return

    parsedArgs = [""] * (len(args)-1)
    for i in range(0, len(args)-1):
        parsedArgs[i] = args[i+1]

    realCommand = args[0]
    if realCommand == "cardlist":
        await cardlist(ctx, parsedArgs)
    elif realCommand == "card":
        await card(ctx, parsedArgs)
    elif realCommand == "commands":
        await commands(ctx, parsedArgs)
    else:
        await card(ctx, args)

CARD_HELP_TEXT = f"If you type \".scribe card <card name>\", I will seek out an image of " \
                 f"the card if I can find it.\n"
async def card(ctx, args):
    """
    Outputs the image of a card to the executed channel based on input card name.
    Will prompt user if input is invalid.
    """
    if len(args) == 0:
        await ctx.send(f"I require the name of a card, {ctx.author.name}.")
        return

    # Condense all card arguments into one full name with underscore seperators
    cardString = "_".join(args)

    cardString.replace(" ", "_")
    fileLocation = findCardImage(cardString, os.getcwd() + "\\card_images\\")

    cardString = cardString.replace("_", " ").lower().title()

    if fileLocation == None:
        await ctx.send(f"I find no record of the card \"{cardString}\" in my collection, {ctx.author.name}.")
        return

    with open(fileLocation + ".png", 'rb') as f:
        picture = discord.File(f)

        # We say behold if we're talking directly to a person for flavour
        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.channel.send(f"BEHOLD {ctx.author.name}, {cardString}!", file=picture)
        else:
            await ctx.channel.send(file=picture)
        return

CARDLIST_HELP_TEXT = f"If you type \".scribe cardlist <class name>\", I will message you a list of " \
                     f"all the cards for that class, if I can find it.\n"
async def cardlist(ctx, args):
    """
    Outputs a list of all cards that a class contains to a DM chat based on input class name.
    Will prompt user if input is invalid.
    """
    if len(args) == 0:
        await ctx.author.send(f"I require the name of a class, {ctx.author.name}.")
        return

    className = args[0].lower().title()

    if className not in ACCEPTED_CLASSES:
        await ctx.author.send(f"I apologise, but I cannot find \"{className}\" in my collection, {ctx.author.name}.")
        return

    classCardList = os.listdir(os.getcwd() + f"\\card_images\\chronicle_rewritten_card_images\\{className}")

    await ctx.author.send(f"I have located these cards belonging to the legend {className} in my collection")
    longCardString = ""
    for card in classCardList:
        longCardString += os.path.splitext(card.replace("_", " "))[0] + "\n"
    await ctx.author.send(f"{longCardString}")
    return 

COMMANDHELP_HELP_TEXT = f"If you type \".scribe commands\", I will output this list of commands again.\n"
async def commandHelp(ctx, *args):
    """
    Outputs a list of documentation.
    """
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        ctx.channel.send(f"I've messaged {ctx.author.name} a list of tasks I can perform.")
    helpString = "Here is a helpful list of user commands\n"
    helpString += PIPE_HELP_TEXT + "\n"
    helpString += CARD_HELP_TEXT + "\n"
    helpString += CARDLIST_HELP_TEXT + "\n"
    helpString += COMMANDHELP_HELP_TEXT + "\n"
    await ctx.author.send(f"Here are all the tasks I can perform, {ctx.author.name}.")
    await ctx.author.send(f"{helpString}")

# Actually run the bot
bot.run(TOKEN)
