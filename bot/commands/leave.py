from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from database.client import supabase
from utils.logger import logger
from voice.voice_module import VoiceModule


class LeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot, voice_module: VoiceModule):
        self.bot = bot
        self.voice_module = voice_module

    @app_commands.command(name="leave", description="Leave the voice channel")
    @app_commands.default_permissions(connect=True)
    async def leave(self, interaction: discord.Interaction) -> None:
        if not interaction.guild_id:
            await interaction.response.send_message(
                "This command can only be used in a server!", ephemeral=True
            )
            return

        guild_id = interaction.guild_id

        bot_vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not self.voice_module.is_connected(guild_id) and not bot_vc:
            await interaction.response.send_message(
                "I'm not in a voice channel!", ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            meeting_id = self.voice_module.get_meeting_id(guild_id)
            if meeting_id:
                end_time = datetime.now(timezone.utc)

                resp = await self.bot.loop.run_in_executor(
                    None,
                    lambda: supabase.from_("meetings")
                        .select("start_time")
                        .eq("id", meeting_id)
                        .maybeSingle()
                        .execute(),
                )

                duration_seconds = 0
                if resp.data and resp.data.get("start_time"):
                    start_dt = datetime.fromisoformat(resp.data["start_time"])
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                    duration_seconds = max(0, int((end_time - start_dt).total_seconds()))

                await self.bot.loop.run_in_executor(
                    None,
                    lambda: supabase.from_("meetings")
                        .update({
                            "end_time": end_time.isoformat(),
                            "duration": duration_seconds,
                            "status": "completed",
                        })
                        .eq("id", meeting_id)
                        .execute(),
                )
                logger.info(
                    "Meeting closed",
                    meeting_id=meeting_id,
                    duration_seconds=duration_seconds,
                    guild_id=guild_id,
                )

            if not self.voice_module.is_connected(guild_id) and bot_vc:
                bot_vc.stop_listening()
                await bot_vc.disconnect()
            else:
                await self.voice_module.leave(guild_id)

            await interaction.followup.send("Left the voice channel!")

        except Exception as exc:
            logger.error("Leave command failed", error=str(exc), guild_id=guild_id)
            await interaction.followup.send("Failed to leave the voice channel.")
