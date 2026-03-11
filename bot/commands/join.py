from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from database.client import supabase
from utils.logger import logger
from voice.voice_module import VoiceModule


class JoinCog(commands.Cog):
    def __init__(self, bot: commands.Bot, voice_module: VoiceModule):
        self.bot = bot
        self.voice_module = voice_module

    @app_commands.command(name="join", description="Join your voice channel and start recording")
    @app_commands.default_permissions(connect=True)
    async def join(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server!", ephemeral=True
            )
            return

        member = interaction.user
        if not isinstance(member, discord.Member) or not member.voice or not member.voice.channel:
            await interaction.response.send_message(
                "You need to be in a voice channel first!", ephemeral=True
            )
            return

        voice_channel = member.voice.channel
        guild_id = interaction.guild_id

        bot_member = interaction.guild.me
        perms = voice_channel.permissions_for(bot_member)
        if not perms.connect or not perms.speak:
            await interaction.response.send_message(
                "I need permission to join and speak in your voice channel!",
                ephemeral=True,
            )
            return

        if self.voice_module.is_connected(guild_id):
            await interaction.response.send_message(
                "I'm already in a voice channel on this server! Use `/leave` first.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            await self.voice_module.join(
                voice_channel=voice_channel,
                text_channel=interaction.channel,
            )

            # Make sure this server has a record in the database. We upsert so
            # running /join multiple times (or on a fresh DB) never errors out.
            await self.bot.loop.run_in_executor(
                None,
                lambda: supabase.table("servers").upsert({
                    "discord_id": str(guild_id),
                    "name": interaction.guild.name,
                    "owner_id": str(interaction.guild.owner_id or ""),
                    "bot_installed": True,
                }, on_conflict="discord_id").execute(),
            )

            now = datetime.now(timezone.utc)
            resp = await self.bot.loop.run_in_executor(
                None,
                lambda: supabase.table("meetings").insert({
                    "guild_id": str(guild_id),
                    "channel_id": str(voice_channel.id),
                    "start_time": now.isoformat(),
                    "title": f"Meeting on {now.date().isoformat()}",
                    "status": "in_progress",
                }).execute(),
            )

            if resp.data:
                self.voice_module.track_meeting(guild_id, resp.data[0]["id"])
                logger.info("Meeting created", meeting_id=resp.data[0]["id"], guild_id=guild_id)
            else:
                logger.error("Failed to create meeting record", guild_id=guild_id)

            await interaction.followup.send("Joined! Transcripts will appear here as people speak.")

        except Exception as exc:
            logger.error("Join command failed", error=str(exc), guild_id=guild_id)
            if self.voice_module.is_connected(guild_id):
                try:
                    await self.voice_module.leave(guild_id)
                except Exception:
                    pass
            await interaction.followup.send("Failed to join the voice channel. Please try again.")
