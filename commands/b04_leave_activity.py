import discord
from utils.interfaces import IBot
from utils.persistence import get_activities, remove_activity_member_rel

def add_command_to(bot : IBot):
    @bot.tree.command(name="leave_activity", description="leave an Activity")
    @discord.app_commands.describe(activity_name="the name of the Activity")
    async def leave_activity(
        interaction: discord.Interaction,
        activity_name: str,
    ):
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

        deleted_rows = remove_activity_member_rel(guild_id, activity_name, interaction.user.id)
        if deleted_rows == 0:
            await interaction.response.send_message(
                f"{interaction.user.mention} was not a member of the Activity",
                ephemeral=True,
            )
            return

        json = { "activity_name" : activity_name }

        await interaction.response.send_message(
            f"leave_activity instruction received: \n{json}",
            ephemeral=True,
        )
