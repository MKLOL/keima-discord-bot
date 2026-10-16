import discord
from utils.interfaces import IBot
from utils.persistence import get_connection, get_activities, get_activity_member_rels
from utils.authorisation import is_server_owner

def _change_core_status(guild_id, activity_name, member_id, core_flag):
    connection = get_connection(guild_id)
    connection.execute("""
        UPDATE activity_member_rel
        SET core_flag=?
        WHERE activity_name=?
            AND member_id=?
    """,
        ( '01'[0 + core_flag], activity_name, member_id, )
    )
    connection.commit()
    connection.close()

def add_command_to(bot : IBot):
    @bot.tree.command(name="change_core_status", description="set/unset a member as a core member")
    @discord.app_commands.describe(activity_name="the name of the Activity", member="the member", core_flag="1 = set as core, 0 = unset as core")
    async def change_core_status(
        interaction: discord.Interaction,
        activity_name: str,
        member: discord.Member,
        core_flag: str,
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

        activity_member_rels = get_activity_member_rels(guild_id)
        try:
            activity_member_rel = [activity_member_rel for activity_member_rel in activity_member_rels if member.id == activity_member_rel.member_id and activity_name == activity_member_rel.activity_name][0]
        except:
            await interaction.response.send_message(
                f"{member.mention} is not a member of the Activity",
                ephemeral=True,
            )
            return

        core_flag = core_flag.strip()
        if core_flag not in '10':
            await interaction.response.send_message(
                "core_flag must be 1 or 0",
                ephemeral=True,
            )
            return

        _core_flag = (core_flag == '1')
        if activity_member_rel.core_flag ^ _core_flag == False:
            await interaction.response.send_message(
                "command failed: the specified value of core_flag is already the current value",
                ephemeral=True,
            )
            return

        _change_core_status(guild_id, activity_name, member.id, _core_flag)

        json = { "activity_name" : activity_name, "member" : member, "core_flag" : core_flag }

        await interaction.response.send_message(
            f"change_core_status instruction received: \n{json}",
            ephemeral=True,
        )
