```
██╗  ██╗███████╗██████╗  █████╗ ██████╗  ██████╗ ████████╗
██║  ██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
███████║█████╗  ██║  ██║███████║██████╔╝██║   ██║   ██║
██╔══██║██╔══╝  ██║  ██║██╔══██║██╔══██╗██║   ██║   ██║
██║  ██║███████╗██████╔╝██║  ██║██████╔╝╚██████╔╝   ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝   ╚═╝
```

A Discord bot that joins your voice channel, transcribes everything in real time, posts each line to a text channel, and saves the full transcript to Supabase.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat)](LICENSE) [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new) [![Powered by Deepgram](https://img.shields.io/badge/transcription-Deepgram-black?style=flat)](https://deepgram.com)

---

## 📦 What you'll need

- A Discord bot token — free
- A Deepgram API key — free ($200 credit included)
- A Supabase project — free tier works

---

## ⚡ Quick start

```bash
git clone https://github.com/ana1337x/hedabot-oss
cd hedabot-oss
cp .env.example .env
# Fill in your credentials in .env, then:
docker compose up
```

First time? Read the [full setup guide](SETUP.md) — it walks through every step with no coding experience required.

---

## ☁️ Deploy to the cloud

**Fly.io (free tier)**
```bash
fly auth login
fly launch
fly secrets set DISCORD_TOKEN=... DEEPGRAM_API_KEY=... SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=...
fly deploy
```

**Railway**

1. Fork this repo, then create a new Railway project from your fork
2. Set the four environment variables in the Railway dashboard
3. Railway detects the Dockerfile and deploys automatically

---

## 💬 Commands

| Command | What it does |
|---------|-------------|
| `/join` | Bot joins your voice channel and starts transcribing |
| `/leave` | Bot stops and leaves |

---

## ⚙️ How it works

1. `/join` — bot connects to your voice channel and creates a meeting record in Supabase
2. As people talk, each line of speech is posted to the text channel and saved to your database
3. `/leave` — bot disconnects and marks the meeting as complete

Your Supabase project ends up with a `meetings` table and a `transcripts` table you can query, export, or build on top of however you like. Works with Discord's DAVE voice encryption (mandatory since March 2026).

---

## 📄 License

MIT
