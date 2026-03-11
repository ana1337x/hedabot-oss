"""
AudioSink — discord-ext-voice-recv AudioSink subclass.

For each user who speaks:
  1. Opus packet arrives in write() from voice-recv's audio thread
  2. Per-user discord.opus.Decoder decodes it to stereo 16-bit PCM @ 48 kHz
  3. Stereo is converted to mono (average L+R)
  4. Mono PCM is sent to a Deepgram streaming WebSocket
  5. On a final transcript result, asyncio.run_coroutine_threadsafe() fires
     the async on_transcript callback back on the bot's event loop

Deepgram handles silence detection and stream management — no manual restart
loops or timeout tracking needed on our end.
"""

import asyncio
import struct
import threading
import time
from typing import Callable

import discord
from discord.ext import voice_recv
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

import config
from utils.logger import logger


_deepgram = DeepgramClient(api_key=config.DEEPGRAM_API_KEY)

_LIVE_OPTIONS = LiveOptions(
    model="nova-3",
    encoding="linear16",
    sample_rate=48000,
    channels=1,
    language="en-US",
    punctuate=True,
    interim_results=True,
    endpointing=400,  # ms of silence before Deepgram finalizes the current utterance
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stereo_to_mono(stereo: bytes) -> bytes:
    """Convert stereo int16 PCM to mono by averaging left and right channels.

    Discord always gives us stereo audio (two channels), but we only need one
    for transcription. We average both instead of dropping one so nothing gets lost.
    """
    n_frames = len(stereo) // 4
    mono = bytearray(n_frames * 2)
    for i in range(n_frames):
        left = struct.unpack_from("<h", stereo, i * 4)[0]
        right = struct.unpack_from("<h", stereo, i * 4 + 2)[0]
        avg = (left + right) // 2
        struct.pack_into("<h", mono, i * 2, avg)
    return bytes(mono)


# ---------------------------------------------------------------------------
# Per-user transcription session
# ---------------------------------------------------------------------------

class _UserSession:
    def __init__(
        self,
        user_id: int,
        guild_id: int,
        event_loop: asyncio.AbstractEventLoop,
        on_transcript: Callable,  # async def(guild_id, user_id, text, confidence)
    ):
        self.user_id = user_id
        self.guild_id = guild_id
        self.loop = event_loop
        self.on_transcript = on_transcript

        self.decoder = discord.opus.Decoder()
        self._connection = None
        self._lock = threading.Lock()
        self._pending: list[bytes] = []  # audio buffered while the connection is starting

        # One Deepgram WebSocket per user, opened the first time they say something.
        # We start the connection in a background thread so we don't block incoming
        # audio while the WebSocket handshake is happening.
        thread = threading.Thread(
            target=self._connect,
            name=f"dgram-{user_id}",
            daemon=True,
        )
        thread.start()
        logger.info("Voice session started", user_id=user_id, guild_id=guild_id)

    def _connect(self) -> None:
        # Try up to three times in case of a transient network hiccup at startup.
        for attempt in range(1, 4):
            connection = _deepgram.listen.websocket.v("1")

            def on_transcript(_conn, result, **kwargs):
                try:
                    alt = result.channel.alternatives[0]
                    text = alt.transcript.strip()
                    confidence = alt.confidence
                    # speech_final fires when Deepgram's endpointing triggers — a complete utterance.
                    # is_final alone can fire mid-sentence; we wait for speech_final for cleaner lines.
                    if result.speech_final and text:
                        logger.info(
                            "Transcription",
                            user_id=self.user_id,
                            guild_id=self.guild_id,
                            text=text,
                            confidence=round(confidence, 3),
                        )
                        # Fire the callback on the bot's event loop. Deepgram calls this from
                        # its own internal thread, and asyncio doesn't like outside callers.
                        asyncio.run_coroutine_threadsafe(
                            self.on_transcript(self.guild_id, self.user_id, text, confidence),
                            self.loop,
                        )
                except Exception as exc:
                    logger.warning("Transcript handler error", user_id=self.user_id, error=str(exc))

            connection.on(LiveTranscriptionEvents.Transcript, on_transcript)

            ok = connection.start(_LIVE_OPTIONS)
            if ok:
                with self._lock:
                    self._connection = connection
                    # Drain any audio that arrived while the connection was starting up.
                    # Usually just the first few frames — we don't want to drop the
                    # beginning of someone's first sentence.
                    for chunk in self._pending:
                        connection.send(chunk)
                    self._pending.clear()
                return

            logger.warning(
                "Deepgram connection attempt failed",
                user_id=self.user_id,
                attempt=attempt,
            )
            time.sleep(attempt)  # back off a little before retrying

        logger.error(
            "Deepgram connection failed after 3 attempts — no transcription for this user",
            user_id=self.user_id,
        )
        with self._lock:
            self._pending.clear()

    def feed(self, opus_bytes: bytes) -> None:
        """Called from voice-recv's audio thread. Decode Opus → mono PCM → Deepgram."""
        try:
            pcm_stereo = self.decoder.decode(opus_bytes)
            pcm_mono = _stereo_to_mono(pcm_stereo)
        except Exception as exc:
            logger.warning("Opus decode error", user_id=self.user_id, error=str(exc))
            return

        with self._lock:
            if self._connection is None:
                self._pending.append(pcm_mono)
            else:
                # Deepgram handles all the buffering on their end — we just pipe audio in.
                self._connection.send(pcm_mono)

    def stop(self) -> None:
        with self._lock:
            conn = self._connection
            self._connection = None
            self._pending.clear()
        if conn:
            try:
                conn.finish()
            except Exception:
                pass
        logger.info("Voice session ended", user_id=self.user_id, guild_id=self.guild_id)


# ---------------------------------------------------------------------------
# AudioSink — discord-ext-voice-recv AudioSink subclass
# ---------------------------------------------------------------------------

class AudioSink(voice_recv.AudioSink):
    """
    Plug into voice_client.listen(sink).
    Manages per-user Deepgram sessions for the duration of a voice call.
    """

    def __init__(
        self,
        guild_id: int,
        event_loop: asyncio.AbstractEventLoop,
        on_transcript: Callable,
    ):
        super().__init__()
        self.guild_id = guild_id
        self.loop = event_loop
        self.on_transcript = on_transcript
        self._sessions: dict[int, _UserSession] = {}

    def wants_opus(self) -> bool:
        return True  # we handle decoding ourselves

    def write(self, user, data: voice_recv.VoiceData) -> None:
        """Called by voice-recv for every incoming (DAVE-decrypted) Opus packet."""
        if user is None:
            return

        user_id = user.id

        if user_id not in self._sessions:
            self._sessions[user_id] = _UserSession(
                user_id=user_id,
                guild_id=self.guild_id,
                event_loop=self.loop,
                on_transcript=self.on_transcript,
            )

        if data.packet.decrypted_data is None:
            return  # silence packet or DAVE session not yet fully negotiated

        self._sessions[user_id].feed(bytes(data.packet.decrypted_data))

    def cleanup(self) -> None:
        """Called by voice-recv when stop_listening() is invoked."""
        for session in self._sessions.values():
            session.stop()
        self._sessions.clear()
