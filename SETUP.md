# Setup Guide

This guide walks you through everything you need to get hedabot running. It's written to be followed alongside Claude or another AI assistant — each step is self-contained so you can paste any section and ask for help.

**Time to complete:** about 20–30 minutes.

---

## What you'll need

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed (for local hosting), **or** a [Fly.io](https://fly.io) or [Railway](https://railway.app) account (for cloud hosting)
- A Discord account with admin access to at least one server
- A credit card is **not** required for any of the free tiers

---

## Step 1 — Create your Discord bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) and click **New Application**
2. Give it a name (e.g. "hedabot") and click **Create**
3. In the left sidebar, click **Bot**
4. Click **Reset Token**, confirm, then copy the token somewhere safe — you'll need it later

> **Gotcha — Privileged Intents:** Scroll down on the Bot page to **Privileged Gateway Intents**. Enable **Server Members Intent** and **Voice States Intent**. Without these, the bot won't know who's in voice channels and will silently fail.

5. In the left sidebar, click **OAuth2**, then **URL Generator**
6. Under **Scopes**, check `bot` and `applications.commands`
7. Under **Bot Permissions**, check:
   - View Channels
   - Connect
   - Speak
   - Send Messages
   - Read Message History
8. Scroll to the bottom — you'll see a generated URL. **Copy it and save it somewhere.** This is your bot's invite link. You'll need it again any time you want to add the bot to another server.
9. Open that URL in your browser. Discord will show you an authorization screen asking which server to add the bot to. Pick your server and click **Authorize**.

> **What you should see:** After clicking Authorize, Discord shows a checkmark and says the bot was added. Open your server and you should see the bot appear in the member list (offline until you start it in Step 5).

> **Gotcha — Slash commands:** After the bot first starts up, slash commands can take up to an hour to appear in Discord. If `/join` doesn't show up right away, wait a bit and try again.

---

## Step 2 — Get a Deepgram API key

1. Go to [console.deepgram.com](https://console.deepgram.com) and create an account (no credit card required)
2. Once logged in, click **API Keys** in the left sidebar
3. Click **Create a New API Key**, give it a name, and copy the key

That's it. Deepgram gives you $200 of free credit when you sign up, which covers a lot of transcription time.

---

## Step 3 — Set up Supabase

1. Go to [supabase.com](https://supabase.com) and create an account
2. Click **New Project**, choose a name and a region close to you, and wait for it to finish setting up (takes about a minute)
3. In the left sidebar, go to **SQL Editor**
4. Open the file `supabase/migrations/001_schema.sql` from this repo, paste the whole thing into the editor, and click **Run**

   You should see "Success. No rows returned." — that means the tables were created.

5. Now get your credentials. Go to **Project Settings → API**:
   - Copy the **Project URL** — this is your `SUPABASE_URL`
   - Under **Project API keys**, copy the **service_role** key (not the anon key) — this is your `SUPABASE_SERVICE_ROLE_KEY`

> **Gotcha — service_role vs anon key:** There are two keys on that page. The `anon` key is for client-side apps. The `service_role` key is what the bot needs because it bypasses row-level security to write data. Keep it out of any public code.

---

## Step 4 — Configure your environment

Copy the example file:

```bash
cp .env.example .env
```

Open `.env` and fill in the four required values:

```
DISCORD_TOKEN=        ← from Step 1
DEEPGRAM_API_KEY=     ← from Step 2
SUPABASE_URL=         ← from Step 3 (Project URL)
SUPABASE_SERVICE_ROLE_KEY=  ← from Step 3 (service_role key)
```

---

## Step 5 — Run the bot

Pick whichever option fits your setup.

### Option A: Docker (local or VPS)

Make sure Docker Desktop is running, then:

```bash
docker compose up
```

The first run will take a few minutes while Docker builds the image. After that it starts in a few seconds. You should see `"hedabot: imports OK"` and then `"Bot ready"` in the logs.

To stop the bot: `Ctrl+C`, then `docker compose down`.

> **Gotcha — keeping it running:** If you want the bot online even when your computer is off, you'll need to run it on a VPS (like a $5/mo DigitalOcean droplet) or use one of the cloud options below.

---

### Option B: Fly.io (free cloud hosting)

Fly.io has a free tier that's enough to keep the bot running 24/7.

1. Install the Fly CLI: [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/)
2. Log in:
   ```bash
   fly auth login
   ```
3. From the `hedabot-oss` folder, launch the app:
   ```bash
   fly launch
   ```
   When it asks if you want to deploy now, say **no** — you need to set your secrets first.

4. Set your credentials:
   ```bash
   fly secrets set \
     DISCORD_TOKEN="your-token-here" \
     DEEPGRAM_API_KEY="your-key-here" \
     SUPABASE_URL="your-url-here" \
     SUPABASE_SERVICE_ROLE_KEY="your-key-here"
   ```

5. Deploy:
   ```bash
   fly deploy
   ```

6. Check the logs to make sure it started:
   ```bash
   fly logs
   ```

> **Gotcha — app name:** The `fly.toml` file has `app = "hedabot"` at the top. If that name is already taken on Fly.io, `fly launch` will prompt you to choose a different one. Just say yes and it'll update the file.

---

### Option C: Railway

1. Create a [Railway](https://railway.app) account and connect your GitHub
2. Fork this repo to your GitHub account
3. In Railway, click **New Project → Deploy from GitHub repo** and select your fork
4. Railway will detect the Dockerfile automatically
5. Click **Variables** and add the four required env vars:
   - `DISCORD_TOKEN`
   - `DEEPGRAM_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
6. Click **Deploy**

> **Gotcha — Railway free tier:** Railway's free tier gives 500 hours/month, which isn't enough for a bot that runs 24/7 (that needs ~720 hours). You'll need their Hobby plan ($5/mo) for always-on hosting.

---

## Verify it's working

1. Join a voice channel in your Discord server
2. In any text channel, type `/join`
3. The bot should join your voice channel and reply "Joined!"
4. Say something out loud — you should see a transcript line appear in the text channel within a second or two
5. Type `/leave` to stop

In your Supabase dashboard, go to **Table Editor → meetings** — you should see a row for the session you just ran. The `transcripts` table will have one row per line of speech.

---

## Troubleshooting

**`/join` doesn't show up in Discord**
Slash commands are registered globally and can take up to an hour after first boot. Check that the bot is online (green dot in your server's member list).

**Bot joins but no transcripts appear**
- Check that you gave the bot permission to send messages in the channel you used `/join` from
- Check the bot logs for errors — look for anything mentioning Deepgram or "connection failed"

**"Missing required env vars" on startup**
One of your four required variables is missing or has a typo. Double-check the `.env` file (or Railway/Fly.io Variables panel) against the values in `.env.example`.

**Bot disconnects from voice unexpectedly**
This can happen if the bot loses its internet connection. If you're running locally with Docker, make sure your computer doesn't go to sleep. For always-on hosting use Fly.io or Railway.

**Deepgram errors in logs**
Make sure your `DEEPGRAM_API_KEY` is correct and that you haven't exhausted your free credit. You can check your usage at [console.deepgram.com](https://console.deepgram.com).
