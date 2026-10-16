import discord
from utils.interfaces import IBot
from utils.persistence import get_connection, get_activities, get_activity_member_rels, get_future_sessions
from utils.authorisation import is_activity_core_member
import re
import datetime

async def _propose_session(interaction : discord.Interaction, activity_name, start_time):
    guild_id = interaction.guild_id
    activity_member_rels = [
        activity_member_rel
        for activity_member_rel in get_activity_member_rels(guild_id)
        if activity_name == activity_member_rel.activity_name
    ]

    mentions = ' '.join(f"<@{activity_member_rel.member_id}>" for activity_member_rel in activity_member_rels)
    dt = datetime.datetime.strptime(start_time, "%Y-%m-%d-%H:%M").replace(tzinfo=datetime.timezone.utc)
    message_contents = f"{mentions}\nIf you are available for `{activity_name}` <t:{int(dt.timestamp())}:R>, please react with a :thumbsup: to this message.\nAt the indicated time, if all core members have reacted, all users who have reacted will be mentioned again."

    await interaction.response.send_message(message_contents)
    message = await interaction.original_response()
    message_id = message.id
    channel_id = message.channel.id

    await message.add_reaction("👍")

    connection = get_connection(guild_id)
    connection.execute("""
        INSERT INTO future_session
        VALUES (?, ?, ?, ?)
    """,
        ( activity_name, start_time, message_id, channel_id, )
    )
    connection.commit()
    connection.close()

def add_command_to(bot : IBot):
    @bot.tree.command(name="propose_session", description="propose a session for an Activity (core members only)")
    @discord.app_commands.describe(activity_name="the name of the Activity", start_time="the start time (in UTC) of the proposed session, in the format [yyyy-MM-dd-HH:mm]")
    async def propose_session(
        interaction: discord.Interaction,
        activity_name: str,
        start_time: str,
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
        try:
            activity = [activity for activity in activities if activity_name == activity.activity_name][0]
        except:
            await interaction.response.send_message(
                "the Activity does not exist",
                ephemeral=True,
            )
            return

        if activity.archived_flag:
            await interaction.response.send_message(
                "cannot propose sessions for archived Activities",
                ephemeral=True,
            )
            return

        future_sessions = get_future_sessions(guild_id)
        try:
            future_session = [future_session for future_session in future_sessions if activity_name == future_session.activity_name][0]
            channel_id = future_session.channel_id
            message_id = future_session.message_id
            link_to_message = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
            await interaction.response.send_message(
                f"there is already a proposed session for the Activity: {link_to_message}",
                ephemeral=True,
            )
            return
        except:
            pass

        start_time = '-'.join(start_time.split()).replace('[','').replace(']','')
        pattern = r"\d{4}-\d{2}-\d{2}-\d{2}:\d{2}"

        if not re.fullmatch(pattern, start_time):
            await interaction.response.send_message(
                "start_time should be in the format [yyyy-MM-dd-HH:mm]",
                ephemeral=True,
            )
            return

        try:
            dt = datetime.datetime.strptime(start_time, "%Y-%m-%d-%H:%M").replace(tzinfo=datetime.timezone.utc)
        except:
            await interaction.response.send_message(
                "invalid time: {start_time}",
                ephemeral=True,
            )
            return

        if dt < datetime.datetime.now(datetime.timezone.utc):
            await interaction.response.send_message(
                "start_time must be in the future",
                ephemeral=True,
            )
            return

        await _propose_session(interaction, activity_name, start_time)
