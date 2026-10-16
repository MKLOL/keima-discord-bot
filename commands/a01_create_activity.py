import discord
from utils.interfaces import IBot
from utils.persistence import get_connection, get_activities, add_activity_member_rel
from utils.authorisation import is_server_owner

def _insert_activity(guild_id, activity_name, description):
    connection = get_connection(guild_id)
    connection.execute("""
        INSERT INTO activity
        VALUES (?, ?, ?)
    """,
        ( activity_name, description, archived_flag:=0, )
    )
    connection.commit()
    connection.close()

def add_command_to(bot : IBot):
    @bot.tree.command(name="create_activity", description="create a new Activity")
    @discord.app_commands.describe(activity_name="the name of the Activity", description="a description of the Activity")
    async def create_activity(
        interaction: discord.Interaction,
        activity_name: str,
        description: str | None = '',
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
                "the Activity's name must not contain whitespace",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild_id
        if guild_id not in bot.guild_ids:
            bot.guild_ids.append(guild_id)
        activities = get_activities(guild_id)
        if any(activity_name == activity.activity_name for activity in activities):
            await interaction.response.send_message(
                "the Activity already exists",
                ephemeral=True,
            )
            return

        _insert_activity(guild_id, activity_name, description)
        add_activity_member_rel(guild_id, activity_name, interaction.user.id, core_flag:='1')

        json = { "activity_name" : activity_name, "description" : description }

        await interaction.response.send_message(
            f"create_activity instruction received: \n{json}",
            ephemeral=True,
        )
