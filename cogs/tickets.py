import discord
from discord.ext import commands
import yaml
import asyncio
import logging
import time

# Configure logging
log_filename = f"./logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

class TicketSystem(commands.Cog):
    """
    This is the main class for ticket-related commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.load_config()
        self.log_file = f"logs/log_{time.strftime('%Y%m%d-%H%M%S')}.log"

    def load_config(self):
        try:
            with open('conf/config.yaml', 'r') as file:
                config = yaml.safe_load(file)
                if not isinstance(config, dict):
                    logging.error("Config file is not a valid YAML dictionary.")
                    return None
                return config
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
            return None

    async def cog_load(self):
        self.bot.add_view(TicketView(self.config))
        self.bot.add_view(Close())

    @commands.hybrid_command(aliases=['tick', 'ticket', 'support'])
    @commands.has_permissions(administrator=True)
    async def open_ticket(self, ctx: commands.Context):
        try:
            await ctx.send(content="Please select a ticket type", view=TicketView(self.config))
        except Exception as e:
            logging.error(f"Failed to open ticket: {e}")

class Ticket(discord.ui.Select):
    def __init__(self, config):
        self.config = config
        options = [
            discord.SelectOption(label="Order", description="Order issue", value="Order"),
            discord.SelectOption(label="Issue", description="General issue", value="Issue"),
            discord.SelectOption(label="Partnership", description="Partnership inquiry", value="Partnership"),
            discord.SelectOption(label="Bot Issue", description="Bot-related issue", value="Bot Issue")
        ]

        super().__init__(placeholder='Choose a type of ticket...', min_values=1, max_values=1, custom_id="Tick:panel", options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.config is None:
                logging.error("Configuration is not loaded.")
                await interaction.response.send_message("Configuration error. Please contact an administrator.", ephemeral=True)
                return
            
            if interaction.guild is None:
                logging.error("Guild not found.")
                await interaction.response.send_message("This command cannot be used in direct messages.", ephemeral=True)
                return

            categ = discord.utils.get(interaction.guild.categories, id=self.config['tickets']['category_id'])
            if not categ:
                logging.error("Category not found.")
                await interaction.response.send_message("There was an error creating your ticket. Please try again later.", ephemeral=True)
                return

            await interaction.response.send_message("Creating a ticket for you, this may take a while!", ephemeral=True)
            ticket_channel_name = self.config['tickets']['ticket_name'].format(user=interaction.user.name)
            ticket_channel = await categ.create_text_channel(name=ticket_channel_name)

            role_id = self.config['tickets']['unifiedSupportRole']
            if not role_id:
                logging.error("Unified Role ID not found.")
                await interaction.followup.send("There was an error creating your ticket. Please try again later.", ephemeral=True)
                return

            role = interaction.guild.get_role(role_id)
            if not role:
                logging.error("Role not found.")
                await interaction.followup.send("There was an error creating your ticket. Please try again later.", ephemeral=True)
                return

            if isinstance(interaction.user, discord.Member):
                await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
            await ticket_channel.set_permissions(role, view_channel=True, send_messages=True)

            view = Close()
            await ticket_channel.send(f"{interaction.user.mention} | <@&{role_id}>")

            ticket_message = self.config['tickets']['ticket_message'].format(user=interaction.user.mention)
            embed = discord.Embed(title=f"{interaction.guild.name} Ticker", description=ticket_message)
            await ticket_channel.send(embed=embed, view=view)
        except Exception as e:
            logging.error(f"Failed to create ticket: {e}")

class TicketView(discord.ui.View):
    def __init__(self, config):
        super().__init__(timeout=None)
        self.add_item(Ticket(config))

class Close(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id='del')
    async def tick_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.guild_permissions.manage_channels: #type: ignore
                await interaction.response.send_message('Deleting the channel in 10 seconds!', ephemeral=True)
                await asyncio.sleep(10)
                if isinstance(interaction.channel, discord.abc.GuildChannel):
                    await interaction.channel.delete()
                    self.value = True
            else:
                await interaction.response.send_message('You are missing permissions to delete the channel!', ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to close ticket: {e}")

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(TicketSystem(bot))
        logging.info("Tickets cog loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load Tickets cog: {e}")