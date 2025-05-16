import discord
import requests
from discord import app_commands
from discord.ext import commands
import enum
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guild_reactions = True
intents.reactions = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)  # commands.when_mentioned_or("!") is used to make the bot respond to !ping and @bot ping

async def setup_hook() -> None:  # This function is automatically called before the bot starts
    await bot.tree.sync()   # This function is used to sync the slash commands with Discord it is mandatory if you want to use slash commands

bot.setup_hook = setup_hook  # Not the best way to sync slash commands, but it will have to do for now. A better way is to create a command that calls the sync function.

@bot.event
async def on_ready() -> None:  # This event is called when the bot is ready
    print(f"Logged in as {bot.user}")

class Type(str, enum.Enum):
    Likes = "likes"
    Downloads = "downloads"
    Views = "views"
    Updates = "updates"
    Thanks = "thanks"

def gbembed(emoji: str, value: Type, amount: int):
    return discord.Embed(
        title=f"{value.name}",
        description=f"{emoji} {format(amount, ',')}",
        color=discord.Color.from_rgb(250, 228, 88),
    )
@bot.tree.command(name="gb", description="Interacts with the gamebanana api.")
@app_commands.describe(submission_id="The submission you want the api to get.")
@app_commands.describe(type="The amount you want to get from the api.")
async def gb(inter: discord.Interaction, submission_id: str, type: Type) -> None:
   if type == Type.Likes:
       url = requests.get(f"https://gamebanana.com/apiv11/Mod/{submission_id}?_csvProperties=_nLikeCount")
       data = url.json()
       likes = data["_nLikeCount"]
       await inter.response.send_message(embed=gbembed(":thumbsup:", Type.Likes, likes))
   elif type == Type.Thanks:
       url = requests.get(f"https://gamebanana.com/apiv11/Mod/{submission_id}?_csvProperties=_nThanksCount")
       data = url.json()
       thanks = data["_nThanksCount"]
       await inter.response.send_message(embed=gbembed(":heart:", Type.Thanks, thanks))
   elif type == Type.Views:
         url = requests.get(f"https://gamebanana.com/apiv11/Mod/{submission_id}?_csvProperties=_nViewCount")
         data = url.json()
         views = data["_nViewCount"]
         await inter.response.send_message(embed=gbembed(":eye:", Type.Views, views))
   elif type == Type.Downloads:
       url = requests.get(f"https://gamebanana.com/apiv11/Mod/{submission_id}?_csvProperties=_nDownloadCount")
       data = url.json()
       downloads = data["_nDownloadCount"]
       await inter.response.send_message(embed=gbembed(":floppy_disk:", Type.Downloads, downloads)) 
   elif type == Type.Updates:
        url = requests.get(f"https://gamebanana.com/apiv11/Mod/{submission_id}/Updates?_nPage=1&_nPerpage=10")
        data = url.json()
        updates = data["_aMetadata"]["_nRecordCount"]
        await inter.response.send_message(embed=gbembed(":arrows_counterclockwise:", Type.Updates, updates))
@bot.event
async def on_reaction_add(reaction, user):  
    if str(reaction) == "📌":
        if reaction.message.author == user:
            await reaction.message.pin()
            await reaction.remove(user) 
@bot.tree.command(name="rename", description="Renames the currently open forum to what you specify.")
@app_commands.describe(name="The name you want to rename the forum to.")
@app_commands.checks.cooldown(1, 600, key=lambda i: (i.user.id,))
async def rename(inter: discord.Interaction, name: str) -> None:
        if inter.channel.type == discord.ChannelType.public_thread:
                await inter.channel.edit(name=name)
                await inter.response.send_message(f"Renamed the thread to {name}", ephemeral=True)
        else:
                await inter.response.send_message("This command can only be used in a thread.", ephemeral=True)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
     if isinstance(error, app_commands.CommandOnCooldown):
          await interaction.response.send_message(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
bot.run(token)
