import discord
from discord.ext import commands
from discord.ui import Button, View
import sqlite3
import yaml

# Load configuration from YAML file
with open('conf/config.yaml') as file:
    config = yaml.safe_load(file)

suggestions_id = config['suggestion']['channel_id']

class Suggestions(commands.Cog):
    """
    Suggestion command and related functions.
    """
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel_id = suggestions_id
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        # Use sqlite3 for database operations
        with sqlite3.connect("./db/suggestions.db") as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion TEXT,
                    message_link TEXT
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    user_id INTEGER,
                    vote_type TEXT
                )
            """)
            db.commit()

    @commands.hybrid_command(name="suggest")
    async def suggest(self, ctx, *, suggestion: str):
        """
        Submits a suggestion and displays it in an embed with voting buttons.
        """
        embed = discord.Embed(description=suggestion, color=discord.Color.blue())
        embed.set_author(name=f"Suggestion from {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.add_field(name="Upvotes", value="0", inline=True)
        embed.add_field(name="Downvotes", value="0", inline=True)
        embed.add_field(name="Nota", value="0", inline=True)

        # Create buttons
        upvote_button = Button(emoji="<:upvote:1259171536053735424>", custom_id="upvote")
        downvote_button = Button(emoji="<:downvote:1259171762831364107>", custom_id="downvote")
        nota_button = Button(emoji="<:red_dot:1259172069497897070>", custom_id="nota")

        # Add buttons to a view
        view = View()
        view.add_item(upvote_button)
        view.add_item(downvote_button)
        view.add_item(nota_button)

        # Send the suggestion embed with buttons
        suggestion_channel = self.bot.get_channel(self.suggestion_channel_id)
        message = await suggestion_channel.send(embed=embed, view=view)

        # Store the suggestion message link in history
        with sqlite3.connect("./db/suggestions.db") as db:
            db.execute("INSERT INTO suggestions (suggestion, message_link) VALUES (?, ?)", (suggestion, message.jump_url))
            db.commit()

        # Update embed counts on button press
        async def button_callback(interaction: discord.Interaction):
            user_id = interaction.user.id
            message_id = message.id
            vote_type = interaction.data['custom_id'] #type: ignore

            with sqlite3.connect("./db/suggestions.db") as db:
                cursor = db.cursor()

                # Check if the user has already voted for this suggestion
                cursor.execute("SELECT vote_type FROM votes WHERE message_id = ? AND user_id = ?", (message_id, user_id))
                existing_vote = cursor.fetchone()

                if existing_vote:
                    if existing_vote[0] == vote_type:
                        # Remove the user's vote
                        cursor.execute("DELETE FROM votes WHERE message_id = ? AND user_id = ?", (message_id, user_id))
                        db.commit()
                        await interaction.response.send_message("Your vote has been deducted.", ephemeral=True)
                    else:
                        # The user has already voted for a different type
                        await interaction.response.send_message(f"You've already voted for {existing_vote[0]}.", ephemeral=True)
                        return
                else:
                    # Add the user's vote
                    cursor.execute("INSERT INTO votes (message_id, user_id, vote_type) VALUES (?, ?, ?)", (message_id, user_id, vote_type))
                    db.commit()
                    await interaction.response.send_message("Your vote has been added.", ephemeral=True)

                # Update the embed counts
                cursor.execute("SELECT vote_type, COUNT(*) FROM votes WHERE message_id = ? GROUP BY vote_type", (message_id,))
                votes = cursor.fetchall()

                upvotes = sum(count for vote, count in votes if vote == "upvote")
                downvotes = sum(count for vote, count in votes if vote == "downvote")
                nota = sum(count for vote, count in votes if vote == "nota")

                embed.set_field_at(0, name="Upvotes", value=str(upvotes), inline=True)
                embed.set_field_at(1, name="Downvotes", value=str(downvotes), inline=True)
                embed.set_field_at(2, name="Nota", value=str(nota), inline=True)

                # Set the color of the embed based on the vote counts
                if upvotes > downvotes:
                    embed.color = discord.Color.green()
                elif downvotes > upvotes:
                    embed.color = discord.Color.red()
                else:
                    embed.color = discord.Color.blue()

                await message.edit(embed=embed)

        upvote_button.callback = button_callback
        downvote_button.callback = button_callback
        nota_button.callback = button_callback

        await ctx.send(f"Suggestion submitted: {suggestion}", ephemeral=True)

    @commands.hybrid_command(name="suggestions_history")
    @commands.has_permissions(administrator=True)
    async def suggestions_history(self, ctx):
        """
        Retrieves the history of suggestions.
        """
        with sqlite3.connect("./db/suggestions.db") as db:
            cursor = db.execute("SELECT suggestion, message_link FROM suggestions")
            rows = cursor.fetchall()
            if not rows:
                await ctx.send("No suggestions found.")
                return
            embed = discord.Embed(title="Suggestions History", color=discord.Color.blue())
            for row in rows:
                suggestion = row[0]
                message_link = row[1]
                embed.add_field(name="Suggestion", value=suggestion, inline=False)
                embed.add_field(name="Message Link", value=message_link, inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)  # Empty field for spacing
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
