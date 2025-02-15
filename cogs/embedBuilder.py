import discord
from discord import ui
from discord.ext import commands
from discord.ext.commands import Context

def hex_to_color(hex_code: str) -> discord.Color:
    hex_code = hex_code.lstrip('#')
    return discord.Color(int(hex_code, 16))

class EmbedBuilderModal(ui.Modal):
    def __init__(self, builder, field_name: str, placeholder: str, field_label: str, style=discord.TextStyle.short):
        super().__init__(title="Embed Builder")
        self.builder = builder
        self.field_name = field_name
        self.add_item(ui.TextInput(label=field_label, placeholder=placeholder, style=style))

    async def on_submit(self, interaction: discord.Interaction):
        input_value = self.children[0].value #type: ignore
        await getattr(self.builder, f"set_{self.field_name}")(interaction, input_value)

class EmbedFieldModal(ui.Modal):
    def __init__(self, builder, index=None, name="", value="", inline=False):
        super().__init__(title="Embed Field Editor")
        self.builder = builder
        self.index = index
        self.add_item(ui.TextInput(label="Field Name", placeholder="Enter the field name", default=name))
        self.add_item(ui.TextInput(label="Field Value", placeholder="Enter the field value", default=value, style=discord.TextStyle.long))
        self.inline = inline

    async def on_submit(self, interaction: discord.Interaction):
        name = self.children[0].value #type: ignore
        value = self.children[1].value #type: ignore
        inline = self.inline
        if self.index is None:
            self.builder.fields.append((name, value, inline))
        else:
            self.builder.fields[self.index] = (name, value, inline)
        await self.builder.update_embed_preview(interaction)

class EmbedBuilderView(ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.title = ""
        self.description = ""
        self.color = discord.Color.blurple()
        self.author_name = ""
        self.author_icon_url = ""
        self.thumbnail_url = ""
        self.fields = []
        self.footer_text = ""
        self.footer_icon_url = ""
        self.image_url = ""
        self.url = ""

    async def update_embed_preview(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.title, description=self.description, color=self.color, url=self.url)
        embed.set_author(name=self.author_name, icon_url=self.author_icon_url)
        embed.set_thumbnail(url=self.thumbnail_url)
        embed.set_image(url=self.image_url)
        for name, value, inline in self.fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def set_title(self, interaction: discord.Interaction, value: str):
        self.title = value
        await self.update_embed_preview(interaction)

    async def set_description(self, interaction: discord.Interaction, value: str):
        self.description = value
        await self.update_embed_preview(interaction)

    async def set_color(self, interaction: discord.Interaction, value: str):
        try:
            self.color = hex_to_color(value)
            await self.update_embed_preview(interaction)
        except ValueError:
            await interaction.response.send_message("Invalid color hex code.", ephemeral=True)

    async def set_author(self, interaction: discord.Interaction, value: str):
        self.author_name = value
        await self.update_embed_preview(interaction)

    async def set_author_icon(self, interaction: discord.Interaction, value: str):
        self.author_icon_url = value
        await self.update_embed_preview(interaction)

    async def set_thumbnail(self, interaction: discord.Interaction, value: str):
        self.thumbnail_url = value
        await self.update_embed_preview(interaction)

    async def set_footer(self, interaction: discord.Interaction, value: str):
        self.footer_text = value
        await self.update_embed_preview(interaction)

    async def set_footer_icon(self, interaction: discord.Interaction, value: str):
        self.footer_icon_url = value
        await self.update_embed_preview(interaction)

    async def set_image(self, interaction: discord.Interaction, value: str):
        self.image_url = value
        await self.update_embed_preview(interaction)

    async def set_url(self, interaction: discord.Interaction, value: str):
        self.url = value
        await self.update_embed_preview(interaction)

    @ui.button(label="Set Title", style=discord.ButtonStyle.primary, row=0)
    async def set_title_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "title", "Enter the embed title", "Title"))

    @ui.button(label="Set Description", style=discord.ButtonStyle.primary, row=0)
    async def set_description_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "description", "Enter the embed description", "Description", style=discord.TextStyle.long))

    @ui.button(label="Set Color", style=discord.ButtonStyle.primary, row=0)
    async def set_color_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "color", "#7289da", "Color (hex)"))

    @ui.button(label="Set Author", style=discord.ButtonStyle.primary, row=1)
    async def set_author_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "author", "Enter the author name", "Author"))

    @ui.button(label="Set Author Icon", style=discord.ButtonStyle.primary, row=1)
    async def set_author_icon_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "author_icon", "Enter the author icon URL", "Author Icon"))

    @ui.button(label="Set Thumbnail", style=discord.ButtonStyle.primary, row=1)
    async def set_thumbnail_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "thumbnail", "Enter the thumbnail URL", "Thumbnail URL"))

    @ui.button(label="Add/Edit Field", style=discord.ButtonStyle.success, row=2)
    async def add_field_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedFieldModal(self))

    @ui.button(label="Set Footer", style=discord.ButtonStyle.primary, row=2)
    async def set_footer_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "footer", "Enter the footer text", "Footer Text"))

    @ui.button(label="Set Footer Icon", style=discord.ButtonStyle.primary, row=2)
    async def set_footer_icon_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "footer_icon", "Enter the footer icon URL", "Footer Icon URL"))

    @ui.button(label="Set Image", style=discord.ButtonStyle.primary, row=3)
    async def set_image_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "image", "Enter the image URL", "Image URL"))

    @ui.button(label="Set URL", style=discord.ButtonStyle.primary, row=3)
    async def set_url_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EmbedBuilderModal(self, "url", "Enter the URL", "URL"))

class EmbedBuilder(commands.Cog):
    """
    This cog provides functionality to build interactive embeds.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="embedbuilder")
    async def embedbuilder(self, ctx: Context):
        """
        Starts an interactive embed builder.
        """
        view = EmbedBuilderView(self.bot)
        await ctx.send("Interactive Embed Builder started. Use the buttons below to build your embed.", view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedBuilder(bot))


