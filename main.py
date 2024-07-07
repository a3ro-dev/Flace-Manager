# Description: Main file for the bot
import psutil
import yaml
import discord
from discord.ext import commands 
import os 
import logging
from pretty_help import PrettyHelp
import asyncio
import random
import subprocess
import sys
from datetime import datetime, timezone
import platform

with open('conf/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

CLR = config['CLR']
PREFIX = config['creds']['prefix']
OWNER_IDS = config['creds']['owner_ids']
TOKEN = config['creds']['token']

# Set up logging
log_file = f"./logs/{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.log"
logging.basicConfig(filename=log_file,
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

# Create a logger instance
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

# Set up the bot

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        self.launch_time = datetime.now(timezone.utc)  # Moved launch_time initialization here
        super().__init__(
            case_sensitive=True,
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
            owner_ids=OWNER_IDS,
            auto_sync_commands=True,
            help_command=PrettyHelp(case_insensitive=True,
                                    sort_commands=True,
                                    no_category="Sys Commands",
                                    thumbnail_url='https://media.discordapp.net/attachments/1247526752465453057/1259386212041625732/goshikbennor.jpg?ex=668b7e4f&is=668a2ccf&hm=4760ded6b122553aa00ffed52c17055738df8be3d3ab95b4bee6968d618ea756&=',
                                    color=CLR))
        
        self.startup_time = 0  # Moved startup_time initialization here

bot = Bot()

@bot.event
async def on_ready():
    bot.loop.create_task(update_presence())
    link = await bot.guilds[0].text_channels[0].create_invite(max_age=0, max_uses=0, unique=True)
    logger.info(f"-----------------------------------------------------------------------------")
    print(f"{link}")
    # Fixed the issue with bot.user being None by moving the log inside on_ready
    logger.info(f"Logged in as {bot.user.name} | {bot.user.id}") #type: ignore
    logger.info(f"-----------------------------------------------------------------------------")
    await bot.load_extension(f'jishaku')

    logger.info(f"-----------------------------------------------------------------------------")
    logger.info(f"| ✨ | Now loading cogs | ✨ |")
    logger.info(f"-----------------------------------------------------------------------------")   
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{file[:-3]}')
                logger.info(f"| ✅ | Loaded cog: {file}")
            except Exception as e:
                logger.error(f"| ❌ | Error loading cog: {file}")
                logger.error(f"{e}")

    subprocess.call('find . -name "*.pyc" -delete', shell=True)
    subprocess.call('find . -name "__pycache__" -delete', shell=True)

async def update_presence():
    # get system stats
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    machine = platform.machine()
    python_version = platform.python_version()
    discord_version = discord.__version__
    guilds = len(bot.guilds)
    users = len(bot.users)
    uptime = datetime.now(timezone.utc) - bot.launch_time
    arch = platform.architecture()
    name = [f"Memory: {memory_usage}%", f"CPU: {cpu_usage}%", f"Machine: {machine}", f"Python: {python_version}", f"Discord: {discord_version}", f"Guilds: {guilds}", f"Users: {users}", f"Uptime: {uptime}", f"Architecture: {arch}"]
    
    # Fixed the typo in "Steaming" to "Streaming"
    await bot.change_presence(activity=discord.Streaming(name=random.choice(name),
                                                        url="https://www.twitch.tv/flace-manager")
                                                        )
    await asyncio.sleep(5) # change every 5 seconds

@bot.hybrid_command(name='ping', aliases=['pong', 'latency'])
async def ping(ctx):
    """
    Check the bot's latency
    """
    message = await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
    for _ in range(5):
        await asyncio.sleep(2)
        await message.edit(content=f'Pong! {round(bot.latency * 1000)}ms')
    await message.edit(content='Ping complete!')

@bot.hybrid_command(name='shutdown', aliases=['exit', 'stop'])
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    """
    Shutdown the bot
    """
    # Clear pycache
    subprocess.call('find . -name "*.pyc" -delete', shell=True)
    subprocess.call('find . -name "__pycache__" -delete', shell=True)
    
    # Read log file
    with open(log_file, 'r') as file:
        log_content = file.read()
    
    # Create an embed with log file content
    embed = discord.Embed(title="Log File",
                          description=f"""```bash
                          {log_content}```""",
                          color=discord.Color.blue())
    
    # Send the embed
    await ctx.send(embed=embed)
    
    # Shutdown the bot
    await bot.close()
    sys.exit()

@bot.hybrid_command(name='restart', aliases=['reboot', 'reload'])
@commands.has_permissions(administrator=True)
async def restart(ctx):
    """
    Restart the bot
    """
    # Clear pycache
    subprocess.call('find . -name "*.pyc" -delete', shell=True)
    subprocess.call('find . -name "__pycache__" -delete', shell=True)
    
    # Read log file
    with open(log_file, 'r') as file:
        log_content = file.read()
    
    # Create an embed with log file content
    embed = discord.Embed(title="Log File",
                          description=f"""```bash
                          {log_content}```""",
                          color=discord.Color.blue())
    
    # Send the embed
    await ctx.send(embed=embed)
    
    # Restart the bot
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.hybrid_command(name='sync')
async def sync(ctx):
    await ctx.bot.tree.sync()
    await ctx.send("Commands synced.")

bot.run(TOKEN)
