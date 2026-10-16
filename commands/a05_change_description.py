import discord
from utils.interfaces import IBot
from utils.persistence import get_connection, get_activities
from utils.authorisation import is_server_owner, is_activity_core_member

def _change_description(guild_id, activity_name, description):
    connection = get_connection(guild_id)
    connection.execute("""
        UPDATE activity
        SET description=?
        WHERE activity_name=?
    """,
        ( description, activity_name, )
    )
    connection.commit()
    connection.close()

def add_command_to(bot : IBot):
    @bot.tree.command(name="change_description", description="change the description of an Activity")
    @discord.app_commands.describe(activity_name="the name of the Activity", description="new description of the Activity")
    async def change_description(
        interaction: discord.Interaction,
        activity_name: str,
        description: str | None = '',
    ):
        if not is_server_owner(interaction, bot) and not is_activity_core_member(interaction, activity_name):
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

        _change_description(guild_id, activity_name, description)

        json = { "activity_name" : activity_name, "description" : description }

        await interaction.response.send_message(
            f"change_description instruction received: \n{json}",
            ephemeral=True,
        )
