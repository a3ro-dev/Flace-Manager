# import discord
# from discord.ext import commands
# from discord.ui import Modal, TextInput, Button, View

# class ButtonBuilderModal(Modal):
#     def __init__(self, bot):
#         super().__init__(title="Button Builder")
#         self.bot = bot

#         self.channel_id = TextInput(label="Channel ID", placeholder="Enter the channel ID", required=True)
#         self.add_item(self.channel_id)

#         self.button_text = TextInput(label="Button Text", placeholder="Enter the button text", required=True)
#         self.add_item(self.button_text)

#         self.emoji_id = TextInput(label="Emoji ID (Optional)", placeholder="Enter the emoji ID", required=False)
#         self.add_item(self.emoji_id)

#         self.url = TextInput(label="Button URL (Optional)", placeholder="Enter the URL the button should link to", required=False)
#         self.add_item(self.url)

#         self.ephemeral_message = TextInput(label="Ephemeral Message (Optional)", placeholder="Enter the ephemeral message", required=False)
#         self.add_item(self.ephemeral_message)

#         self.embed_message = TextInput(label="Embed Message", placeholder="Enter the embed message", required=True)
#         self.add_item(self.embed_message)

#     async def on_submit(self, interaction: discord.Interaction):
#         try:
#             channel_id = int(self.channel_id.value)
#             button_text = self.button_text.value
#             emoji_id = self.emoji_id.value
#             url = self.url.value
#             ephemeral_message = self.ephemeral_message.value
#             embed_message = self.embed_message.value

#             embed = discord.Embed(description=embed_message, color=discord.Color.blue())

#             view = View()
#             if url:
#                 button = Button(label=button_text, emoji=emoji_id if emoji_id else None, url=url)
#             else:
#                 async def button_callback(interaction: discord.Interaction):
#                     await interaction.response.send_message(ephemeral_message, ephemeral=True)

#                 button = Button(label=button_text, emoji=emoji_id if emoji_id else None)
#                 button.callback = button_callback

#             view.add_item(button)

#             channel = self.bot.get_channel(channel_id)
#             if channel is None:
#                 await interaction.response.send_message("Invalid channel ID.", ephemeral=True)
#                 return
            
#             await channel.send(embed=embed, view=view)
#             await interaction.response.send_message("Button and embed sent successfully.", ephemeral=True)
#         except Exception as e:
#             await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

# class ButtonBuilder(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.hybrid_command(name="button_builder", with_app_command=True)
#     async def button_builder(self, ctx: commands.Context):
#         modal = ButtonBuilderModal(self.bot)
#         await ctx.interaction.response.send_modal(modal)
         
# async def setup(bot):
#     await bot.add_cog(ButtonBuilder(bot))



"""
Note:
- This snippet is a cog that allows users to create buttons with embeds, but it is not complete.
- discord.ext.commands.errors.HybridCommandError: Hybrid command raised an error: Command 'button_builder' raised an exception: ValueError: could not find open space for item
"""
