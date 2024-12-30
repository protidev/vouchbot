import discord
from discord import app_commands
import json
import os

# File paths
CONFIG_PATH = "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "guild_id": "123456789012345678",
    "bot_token": "",
    "presence_activity": "Made by ProtiDEV",
    "watermark": "ProtiDEV",
    "watermark_imagelink": "https://cdn.discordapp.com/attachments/1190998549744341117/1320876112057995264/logo.jpeg"
}

def load_config():
    """Load or create the configuration file."""
    if not os.path.exists(CONFIG_PATH) or os.stat(CONFIG_PATH).st_size == 0:
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print("config.json has been created. Please update it with your bot token and guild ID.")
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print("Corrupted config.json detected. Replaced with default values.")
        return DEFAULT_CONFIG

def save_config(data):
    """Save the configuration to the file."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Load configuration
config = load_config()

# Extract configuration variables
GUILD_ID = config["guild_id"]
BOT_TOKEN = config["bot_token"]
PRESENCE_ACTIVITY = config["presence_activity"]
WATERMARK = config["watermark"]
WATERMARK_IMAGE = config["watermark_imagelink"]

# Check for bot token
if not BOT_TOKEN:
    print("Error: The bot token is not configured in config.json. Please update the file and restart the bot.")
    exit(1)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Initialize the Discord client
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
    name="vouch",
    description="Add a general vouch with stars, a description, and an optional image.",
    guild=discord.Object(id=int(GUILD_ID)),
)
async def vouch(interaction: discord.Interaction, stars: int, description: str, image: discord.Attachment = None):
    if stars < 1 or stars > 5:
        await interaction.response.send_message("Stars must be between 1 and 5.", ephemeral=True)
        return

    total_vouches = increment_vouch()

    stars_str = "\u2b50" * stars
    embed = discord.Embed(
        title=stars_str,
        description=f"**Vouch:**\n{description}",
        color=0xFFD700
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.add_field(name="Client", value=f"{interaction.user.mention}", inline=True)
    embed.add_field(name="Total Vouches", value=str(total_vouches), inline=True)
    embed.add_field(name="Vouched at", value=f"{discord.utils.format_dt(interaction.created_at, style='R')}", inline=True)
    embed.set_footer(text=WATERMARK, icon_url=WATERMARK_IMAGE)

    if image:
        file = await image.to_file()
        embed.set_image(url=f"attachment://{file.filename}")
        await interaction.response.send_message(embed=embed, file=file)
    else:
        await interaction.response.send_message(embed=embed)

def increment_vouch():
    if "total_vouches" not in config:
        config["total_vouches"] = 0
    config["total_vouches"] += 1
    save_config(config)
    return config["total_vouches"]

@client.event
async def on_ready():
    print(f"Bot is starting...")
    guild = client.get_guild(int(GUILD_ID))
    if not guild:
        print(f"Error: Guild with ID {GUILD_ID} not found. Please verify the ID in config.json.")
        return

    await tree.sync(guild=guild)
    print("Bot is ready and commands are synced!")
    await client.change_presence(activity=discord.Game(name=PRESENCE_ACTIVITY))

# Start the bot
client.run(BOT_TOKEN)
