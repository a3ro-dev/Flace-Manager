import discord
from discord.ext import commands
from discord.ext.commands import Context
import platform
import psutil
import cpuinfo
import subprocess
from datetime import datetime
import yaml

with open('conf/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

support_server = config['creds']['support_server']
class BotInfo(commands.Cog):
    """
    Commands related to bot's information
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.now() 

    @commands.hybrid_command(name="botinfo")
    async def botinfo(self, ctx: Context):
        """
        Displays information about the bot.
        """
        bot = self.bot
        guild = ctx.guild

        # Gathering system information
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        current_time = datetime.now()

        cpu_info = cpuinfo.get_cpu_info()
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        # Running neofetch
        try:
            neofetch_output = subprocess.check_output("neofetch --stdout", shell=True).decode()
        except Exception as e:
            neofetch_output = f"Neofetch error: {e}"

        embed = discord.Embed(
            title="🤖 Flace Manager Bot Information 🤖",
            description="Here is some detailed information about the bot and the server it is running on.",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=guild.icon.url if guild else bot.user.avatar.url if bot.user else None)  # type: ignore
        embed.set_footer(text="Flace Manager", icon_url=guild.icon.url if guild else bot.user.avatar.url if bot.user else None)  # type: ignore

        # Basic bot information
        embed.add_field(name="Bot Name", value=bot.user.name, inline=True)  # type: ignore
        embed.add_field(name="Developer", value="[a3ro-dev](https://github.com/a3ro-dev)", inline=True)
        embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)

        # System information
        embed.add_field(name="System Information", value=f"""
        **System:** {uname.system}
        **Node Name:** {uname.node}
        **Release:** {uname.release}
        **Version:** {uname.version}
        **Machine:** {uname.machine}
        **Processor:** {cpu_info['brand_raw']}
        """, inline=False)

        # Uptime information
        embed.add_field(name="Uptime", value=f"""
        **System Boot Time:** {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
        **Current Time:** {current_time.strftime('%Y-%m-%d %H:%M:%S')}
        """, inline=False)

        # Resource usage
        embed.add_field(name="Resource Usage", value=f"""
        **CPU Usage:** {cpu_usage}%
        **Memory Usage:** {memory_info.percent}%
        **Disk Usage:** {disk_info.percent}%
        """, inline=False)

        # Neofetch output
        embed.add_field(name="Neofetch Output", value=f"```{neofetch_output}```", inline=False)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Support Server", url=support_server, emoji='✨'))
        view.add_item(discord.ui.Button(label="Developer GitHub", url="https://github.com/a3ro-dev", emoji='<:github:1256935375679655976>'))

        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="status", description="Displays bot's status information")
    async def status(self, ctx: commands.Context):
        """
        Displays the bot's current operational status.
        """
        # Calculate uptime
        uptime_delta = datetime.now() - self.start_time
        uptime_str = self.format_timedelta(uptime_delta)

        # Get bot latency
        latency_ms = round(self.bot.latency * 1000, 2)

        # Count servers and users
        guild_count = len(self.bot.guilds)
        user_count = sum([guild.member_count for guild in self.bot.guilds if guild.member_count is not None])

        embed = discord.Embed(
            title=" Bot Status ",
            description="Here is the current operational status of the bot.",
            color=discord.Color.blurple()
        )

        if self.bot.user is not None:
            embed.set_thumbnail(url=self.bot.user.avatar.url) #type: ignore
        embed.add_field(name="Uptime", value=uptime_str, inline=False)
        embed.add_field(name="Latency", value=f"{latency_ms}ms", inline=False)
        embed.add_field(name="Servers", value=guild_count, inline=True)
        embed.add_field(name="Users", value=user_count, inline=True)

        await ctx.send(embed=embed)

    def format_timedelta(self, delta):
        """
        Formats a timedelta object into a human-readable string.
        """
        seconds = delta.total_seconds()
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

async def setup(bot: commands.Bot):
    await bot.add_cog(BotInfo(bot))


