import discord
from utils.interfaces import IBot
from utils.persistence import get_activities, add_activity_member_rel
from utils.authorisation import is_server_owner

def add_command_to(bot : IBot):
    @bot.tree.command(name="add_to_activity", description="add member to an Activity")
    @discord.app_commands.describe(activity_name="the name of the Activity", member="the member to be added")
    async def add_to_activity(
        interaction: discord.Interaction,
        activity_name: str,
        member: discord.Member,
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

        add_activity_member_rel(guild_id, activity_name, member.id)

        json = { "activity_name" : activity_name, "member" : member }

        await interaction.response.send_message(
            f"add_to_activity instruction received: \n{json}",
            ephemeral=True,
        )
