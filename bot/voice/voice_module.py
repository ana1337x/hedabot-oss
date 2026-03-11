"""
VoiceModule — central coordinator for voice connections.

Responsibilities:
  - Join / leave voice channels
  - Track the active meeting ID per guild
  - Receive transcription callbacks from AudioSink
  - Save transcripts + speakers to Supabase
  - Send transcription messages to the Discord text channel
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands, voice_recv

from database.client import supabase
from utils.logger import logger
from voice.audio.audio_sink import AudioSink


class VoiceModule:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._voice_clients: dict[int, voice_recv.VoiceRecvClient] = {}
        self._sinks: dict[int, AudioSink] = {}
        self._meetings: dict[int, str] = {}
        self._text_channels: dict[int, discord.TextChannel] = {}

    # ------------------------------------------------------------------
    # Public API (called from commands)
    # ------------------------------------------------------------------

    async def join(
        self,
        voice_channel: discord.VoiceChannel,
        text_channel: discord.TextChannel,
    ) -> None:
        guild_id = voice_channel.guild.id

        if guild_id in self._voice_clients:
            raise RuntimeError("Already connected in this guild.")

        vc = await voice_channel.connect(cls=voice_recv.VoiceRecvClient)

        sink = AudioSink(
            guild_id=guild_id,
            event_loop=asyncio.get_event_loop(),
            on_transcript=self._on_transcript,
        )
        vc.listen(sink)

        self._voice_clients[guild_id] = vc
        self._sinks[guild_id] = sink
        self._text_channels[guild_id] = text_channel

        logger.info("Joined voice channel", guild_id=guild_id, channel_id=voice_channel.id)

    async def leave(self, guild_id: int) -> None:
        vc = self._voice_clients.get(guild_id)
        if not vc:
            raise RuntimeError("Not connected in this guild.")

        vc.stop_listening()
        await vc.disconnect()
        self._cleanup_guild(guild_id)
        logger.info("Left voice channel", guild_id=guild_id)

    def track_meeting(self, guild_id: int, meeting_id: str) -> None:
        self._meetings[guild_id] = meeting_id
        logger.info("Meeting tracked", guild_id=guild_id, meeting_id=meeting_id)

    def get_meeting_id(self, guild_id: int) -> Optional[str]:
        return self._meetings.get(guild_id)

    def is_connected(self, guild_id: int) -> bool:
        vc = self._voice_clients.get(guild_id)
        return vc is not None and vc.is_connected()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _cleanup_guild(self, guild_id: int) -> None:
        self._voice_clients.pop(guild_id, None)
        self._sinks.pop(guild_id, None)
        self._meetings.pop(guild_id, None)
        self._text_channels.pop(guild_id, None)

    async def _on_transcript(
        self,
        guild_id: int,
        user_id: int,
        text: str,
        confidence: float,
    ) -> None:
        meeting_id = self._meetings.get(guild_id)
        if not meeting_id:
            logger.warning("No active meeting — transcript dropped", guild_id=guild_id)
            return

        await asyncio.gather(
            self._save_transcript(guild_id, user_id, text, meeting_id),
            self._send_to_discord(guild_id, user_id, text),
            return_exceptions=True,
        )

    async def _save_transcript(
        self,
        guild_id: int,
        user_id: int,
        text: str,
        meeting_id: str,
    ) -> None:
        loop = asyncio.get_event_loop()
        try:
            guild = self.bot.get_guild(guild_id)
            member = guild.get_member(user_id) if guild else None
            if member is None and guild:
                try:
                    member = await guild.fetch_member(user_id)
                except Exception:
                    pass

            username = member.name if member else str(user_id)
            display_name = member.display_name if member else str(user_id)

            server_resp = await loop.run_in_executor(
                None,
                lambda: supabase.from_("servers")
                    .select("id")
                    .eq("discord_id", str(guild_id))
                    .maybeSingle()
                    .execute(),
            )
            if server_resp.data is None:
                logger.error("Server not found in DB", guild_id=guild_id)
                return
            server_id = server_resp.data["id"]

            meeting_resp = await loop.run_in_executor(
                None,
                lambda: supabase.from_("meetings")
                    .select("speakers")
                    .eq("id", meeting_id)
                    .maybeSingle()
                    .execute(),
            )
            if meeting_resp.data is None:
                logger.error("Meeting not found", meeting_id=meeting_id)
                return

            existing_speakers: list[dict] = meeting_resp.data.get("speakers") or []
            speaker_ids = {s["discord_user_id"] for s in existing_speakers}
            is_new_speaker = str(user_id) not in speaker_ids

            updated_speakers = existing_speakers
            if is_new_speaker:
                updated_speakers = existing_speakers + [{
                    "discord_user_id": str(user_id),
                    "username": username,
                    "display_name": display_name,
                    "first_spoke_at": datetime.now(timezone.utc).isoformat(),
                }]

            ops = [
                lambda: supabase.from_("transcripts").insert({
                    "meeting_id": meeting_id,
                    "speaker_id": str(user_id),
                    "content": text,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "server_id": server_id,
                }).execute(),
                lambda: supabase.from_("speakers").upsert({
                    "discord_user_id": str(user_id),
                    "username": username,
                    "display_name": display_name,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }, on_conflict="discord_user_id").execute(),
            ]
            if is_new_speaker:
                ops.append(
                    lambda: supabase.from_("meetings")
                        .update({"speakers": updated_speakers})
                        .eq("id", meeting_id)
                        .execute()
                )

            results = await asyncio.gather(
                *[loop.run_in_executor(None, op) for op in ops],
                return_exceptions=True,
            )
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    op_name = ["transcript", "speaker", "meeting"][i]
                    logger.error(f"DB write failed ({op_name})", error=str(result), guild_id=guild_id)

        except Exception as exc:
            logger.error("Failed to save transcript", error=str(exc), guild_id=guild_id)

    async def _send_to_discord(self, guild_id: int, user_id: int, text: str) -> None:
        channel = self._text_channels.get(guild_id)
        if channel:
            try:
                # Cap at 1900 chars so we stay well under Discord's 2000 char limit.
                if len(text) > 1900:
                    text = text[:1900] + "…"
                await channel.send(f"🎤 <@{user_id}>: {text}")
            except Exception as exc:
                logger.error("Failed to send Discord message", error=str(exc), guild_id=guild_id)
