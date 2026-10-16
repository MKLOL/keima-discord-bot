import discord
from utils.interfaces import IBot
from utils.persistence import get_activities, remove_future_session
from utils.authorisation import is_activity_core_member

def add_command_to(bot : IBot):
    @bot.tree.command(name="unpropose_session", description="unpropose a session for an Activity (core members only)")
    @discord.app_commands.describe(activity_name="the name of the Activity")
    async def unpropose_session(
        interaction: discord.Interaction,
        activity_name: str,
    ):
        if not is_activity_core_member(interaction, activity_name):
            await interaction.response.send_message(
                "you do not have permission for this command",
                ephemeral=True,
            )
            return
        
        activity_name = activity_name.strip()
        if activity_name != ''.join(activity_name.split()):
            await interaction.response.send_message(
                "Activity names do not contain whitespace",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild_id
        if guild_id not in bot.guild_ids:
            bot.guild_ids.append(guild_id)
        activities = get_activities(guild_id)
        if all(activity_name != activity.activity_name for activity in activities):
            await interaction.response.send_message(
                "the Activity does not exist",
                ephemeral=True,
            )
            return

        deleted_rows = remove_future_session(guild_id, activity_name)
        if deleted_rows == 0:
            await interaction.response.send_message(
                "there is no proposed session for the Activity",
                ephemeral=True,
            )
            return

        json = { "activity_name" : activity_name }

        await interaction.response.send_message(
            f"unpropose_session instruction received: \n{json}",
            ephemeral=True,
        )
