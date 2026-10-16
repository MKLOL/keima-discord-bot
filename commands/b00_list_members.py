import discord
from utils.interfaces import IBot
from utils.persistence import get_activities, get_activity_member_rels

def add_command_to(bot : IBot):
    @bot.tree.command(name="list_members", description="list the members of an Activity")
    @discord.app_commands.describe(activity_name="the name of the Activity")
    async def list_members(
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

        activity_member_rels = [
            activity_member_rel
            for activity_member_rel in get_activity_member_rels(guild_id)
            if activity_name == activity_member_rel.activity_name
        ]

        response = '\n'.join([
            f"`{idx}`:member=<@{activity_member_rel.member_id}>"
                + f",core_flag=`{activity_member_rel.core_flag}`"
            for (idx, activity_member_rel) in enumerate(activity_member_rels)
        ])

        await interaction.response.send_message(
            response or "the Activity has no members",
            ephemeral=True,
        )
