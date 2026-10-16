import discord
from utils.interfaces import IBot
from utils.persistence import get_connection, get_activities, get_future_sessions
from utils.authorisation import is_server_owner
import json

def _delete_activity(guild_id, activity_name):
    # TODO also delete all related entries in the other tables
    # TODO keep track of all deleted info
    connection = get_connection(guild_id)
    connection.execute("""
        DELETE FROM activity
        WHERE activity_name=?
    """,
        ( activity_name, )
    )
    connection.commit()
    connection.close()
    # json.dumps()

def add_command_to(bot : IBot):
    @bot.tree.command(name="delete_activity", description="delete an Activity")
    @discord.app_commands.describe(activity_name="the name of the Activity")
    async def delete_activity(
        interaction: discord.Interaction,
        activity_name: str,
    ):
        if not is_server_owner(interaction, bot):
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

        future_sessions = get_future_sessions(guild_id)
        if any(activity_name == future_session.activity_name for future_session in future_sessions):
            await interaction.response.send_message(
                "cannot delete an Activity that has a proposed session",
                ephemeral=True,
            )
            return

        _delete_activity(guild_id, activity_name)

        json = { "activity_name" : activity_name  }

        await interaction.response.send_message(
            f"delete_activity instruction received: \n{json}",
            ephemeral=True,
        )
