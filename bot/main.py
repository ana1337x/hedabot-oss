"""
hedabot — open source Discord voice transcription bot.

Joins a voice channel, transcribes everything said, posts lines to a text
channel in real time, and saves the full transcript to Supabase.

Transcription is handled by Deepgram. Voice encryption (Discord's DAVE
protocol) is handled by the davey library + a fork of discord-ext-voice-recv.
"""

import asyncio
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

print("hedabot: starting", flush=True, file=sys.stderr)

import discord
from discord.ext import commands

import config
from utils.logger import logger
from voice.voice_module import VoiceModule
from commands.join import JoinCog
from commands.leave import LeaveCog

print("hedabot: imports OK", flush=True, file=sys.stderr)


def _patch_voice_recv_router() -> None:
    """
    Monkey-patch PacketRouter.run() to restart on any exception.

    Discord started encrypting voice audio in early 2026 (they call it DAVE).
    The voice-receive library we use can occasionally trip on malformed packets
    during the DAVE handshake — this makes the router restart instead of dying
    quietly and taking the whole bot down with it.
    """
    import inspect
    import time as _time
    from discord.ext.voice_recv import router as _vr_router

    patched = False
    for _name, _cls in inspect.getmembers(_vr_router, inspect.isclass):
        if hasattr(_cls, "_do_run") and hasattr(_cls, "run"):
            _original_run = _cls.run

            def _resilient_run(self, _orig=_original_run):
                while True:
                    try:
                        _orig(self)
                        return  # exited cleanly (stop event was set)
                    except Exception as exc:
                        for attr in ("_end_thread", "stop_event", "_stop_event", "_stop"):
                            ev = getattr(self, attr, None)
                            if ev is not None and getattr(ev, "is_set", lambda: False)():
                                return
                        print(
                            f"hedabot: PacketRouter restarting after: {exc}",
                            flush=True,
                            file=sys.stderr,
                        )
                        _time.sleep(0.05)

            _cls.run = _resilient_run
            patched = True
            print(
                f"hedabot: patched {_cls.__name__}.run (resilient PacketRouter)",
                flush=True,
                file=sys.stderr,
            )
            break

    if not patched:
        print(
            "hedabot: WARNING — could not patch PacketRouter for resilience",
            flush=True,
            file=sys.stderr,
        )


def _load_opus() -> None:
    """Load libopus for audio decoding.

    libopus has to be loaded manually — discord.py doesn't bundle it.
    We try a few different locations so this works on both Mac (local dev)
    and Linux (Docker / cloud deployments).
    """
    import ctypes.util
    import glob
    import subprocess

    if discord.opus.is_loaded():
        print("hedabot: libopus already loaded", flush=True, file=sys.stderr)
        return

    for name in ["libopus.so.0", "libopus.so", "opus", "libopus-0"]:
        try:
            discord.opus.load_opus(name)
            print(f"hedabot: libopus loaded via name '{name}'", flush=True, file=sys.stderr)
            return
        except Exception:
            pass

    lib = ctypes.util.find_library("opus")
    print(f"hedabot: ctypes.find_library('opus') = {lib!r}", flush=True, file=sys.stderr)
    if lib:
        try:
            discord.opus.load_opus(lib)
            print(f"hedabot: libopus loaded via ctypes path '{lib}'", flush=True, file=sys.stderr)
            return
        except Exception as e:
            print(f"hedabot: ctypes path failed: {e}", flush=True, file=sys.stderr)

    try:
        result = subprocess.run(
            ["find", "/usr", "/lib", "/opt", "-name", "libopus.so*", "-type", "f"],
            capture_output=True, text=True, timeout=10
        )
        found = [p for p in result.stdout.strip().split("\n") if p]
        print(f"hedabot: find libopus: {found}", flush=True, file=sys.stderr)
        for path in found:
            try:
                discord.opus.load_opus(path)
                print(f"hedabot: libopus loaded via find '{path}'", flush=True, file=sys.stderr)
                return
            except Exception:
                continue
    except Exception as e:
        print(f"hedabot: find subprocess failed: {e}", flush=True, file=sys.stderr)

    patterns = [
        "/usr/lib/x86_64-linux-gnu/libopus.so*",
        "/usr/lib/aarch64-linux-gnu/libopus.so*",
        "/usr/lib/*/libopus.so*",
        "/usr/lib/libopus.so*",
        "/usr/local/lib/libopus.so*",
        "/nix/store/*/lib/libopus.so*",
    ]
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            try:
                discord.opus.load_opus(path)
                print(f"hedabot: libopus loaded via glob '{path}'", flush=True, file=sys.stderr)
                return
            except Exception:
                continue

    print("hedabot: ERROR — libopus not found, voice receive will fail", flush=True, file=sys.stderr)


def _start_health_server() -> None:
    """Start a minimal HTTP server for cloud health checks.

    Only starts when PORT is set — Railway and Fly.io set this automatically.
    Skipped entirely when running locally with Docker Compose.
    """
    port_str = os.environ.get("PORT")
    if not port_str:
        return

    port = int(port_str)

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass  # keep the logs clean

    server = HTTPServer(("0.0.0.0", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Health server started", port=port)


async def _setup(bot: commands.Bot, voice_module: VoiceModule) -> None:
    await bot.add_cog(JoinCog(bot, voice_module))
    await bot.add_cog(LeaveCog(bot, voice_module))


def main() -> None:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.voice_states = True

    bot = commands.Bot(
        command_prefix="!",  # not used (slash commands only), but commands.Bot requires it
        intents=intents,
    )

    voice_module = VoiceModule(bot)

    @bot.event
    async def on_ready() -> None:
        await _setup(bot, voice_module)
        await bot.tree.sync()
        logger.info("Bot ready", tag=str(bot.user), guilds=len(bot.guilds))

    @bot.tree.error
    async def on_app_command_error(
        interaction: discord.Interaction, error: discord.app_commands.AppCommandError
    ) -> None:
        logger.error(
            "Unhandled command error",
            command=interaction.command.name if interaction.command else "unknown",
            error=str(error),
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send("Something went wrong.", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "Something went wrong.", ephemeral=True
                )
        except Exception:
            pass

    _patch_voice_recv_router()
    _load_opus()
    _start_health_server()
    logger.info("Starting hedabot")

    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as exc:
        print(f"hedabot: bot.run() raised: {exc}", flush=True, file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
