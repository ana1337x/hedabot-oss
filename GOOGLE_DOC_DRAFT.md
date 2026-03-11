# hedabot Setup Guide
### A Discord bot that transcribes your voice calls and saves them automatically.

**No coding required. Takes about 20–30 minutes.**

This guide will walk you through everything step by step. You'll create four free accounts,
copy some credentials, and deploy the bot. By the end, typing `/join` in your Discord
server will make the bot join your voice channel and start transcribing.

If you get stuck on any step, paste it into Claude or ChatGPT and ask for help.

---

## Before you start — what you'll need

☐ A Discord account with admin access to at least one server
☐ A computer with a web browser
☐ About 20–30 minutes

You do NOT need:
✗ Any coding experience
✗ A credit card (all free tiers used in this guide are genuinely free)
✗ Any software installed on your computer (except for the Fly.io option in Step 5)

---

---

# Step 1 — Create your Discord bot

You'll create a "bot application" on Discord's developer platform. Think of this as
registering the bot as an official app — Discord needs to know it exists before it
can join your server.

**1.1** Go to discord.com/developers/applications and log in with your Discord account.

> 📸 SCREENSHOT 1
> What it should show: The Discord Developer Portal homepage. A dark-themed page with
> the heading "My Applications" and a blue "New Application" button in the top right
> corner. If you have no apps yet, the main area will be empty with a message like
> "You don't have any applications yet."

**1.2** Click the blue **New Application** button in the top right.

**1.3** In the popup that appears, type a name for your bot (e.g. "hedabot" or whatever
you want to call it). Click **Create**.

> 📸 SCREENSHOT 2
> What it should show: A popup/modal dialog box over the Developer Portal. It has a
> text field labeled "NAME" with a cursor in it, a checkbox for agreeing to the terms,
> and a blue "Create" button at the bottom right. The background is darkened.

**1.4** You'll land on the General Information page for your new app. In the left sidebar,
click **Bot**.

> 📸 SCREENSHOT 3
> What it should show: The left sidebar of the Developer Portal with several menu items
> listed vertically. The items include: General Information, OAuth2, Bot, Rich Presence,
> App Testers, and others. "Bot" should be highlighted or you should draw an arrow
> pointing to it.

**1.5** On the Bot page, click **Reset Token**. A warning popup will appear — click
**Yes, do it**. Your token will appear on screen.

> 📸 SCREENSHOT 4
> What it should show: The Bot page. Near the top there is a "TOKEN" section with a
> "Reset Token" button. After clicking it and confirming, the token appears as a long
> string of random characters (e.g. "MTA4NjM3...") with a "Copy" button next to it.
> The token should be visible on screen. Note: blur or black out the actual token value
> in the screenshot — never share yours publicly.

**1.6** Click **Copy** to copy the token. Paste it somewhere safe (a notes app, a text
file on your desktop). **You won't be able to see this token again** once you leave
the page — if you lose it you'll need to reset it again.

---

⚠️ **CALLOUT BOX — Yellow/Warning**
Title: Keep your bot token private
Your bot token is like a password. Anyone who has it can control your bot.
Never share it in a Discord message, post it on GitHub, or put it in a public document.

---

**1.7** Scroll down on the Bot page to find the section called **Privileged Gateway Intents**.
Enable the following two toggles:
- **Server Members Intent**
- **Voice States Intent** (this one may already be on)

Click **Save Changes** at the bottom.

> 📸 SCREENSHOT 5
> What it should show: The lower portion of the Bot page showing the "Privileged Gateway
> Intents" section. There are three toggle switches: Presence Intent, Server Members
> Intent, and Message Content Intent. The Server Members Intent toggle should be shown
> in the ON position (typically shown as a green/blue filled toggle), with the other
> toggles in whatever state they're in. Draw a box or arrow around the Server Members
> Intent toggle.

---

ℹ️ **CALLOUT BOX — Blue/Info**
Title: Why do these intents matter?
Without Server Members Intent, the bot can't see who's in your voice channel — it
would transcribe audio without knowing whose voice it is. Without Voice States Intent,
it can't tell when people join or leave. Both are required.

---

**1.8** In the left sidebar, click **OAuth2**, then click **URL Generator** in the submenu
that appears.

> 📸 SCREENSHOT 6
> What it should show: The left sidebar with OAuth2 expanded to show two sub-items:
> "General" and "URL Generator". URL Generator should be highlighted or have an arrow
> pointing to it.

**1.9** Under **Scopes**, check two boxes: **bot** and **applications.commands**.

> 📸 SCREENSHOT 7
> What it should show: The Scopes section of the URL Generator page. It shows a grid
> of checkboxes with labels like "identify", "email", "bot", "applications.commands",
> etc. The "bot" and "applications.commands" checkboxes should be shown checked (with
> a checkmark or filled blue). Draw boxes around the two checked items.

**1.10** Scroll down to the **Bot Permissions** section that appeared below Scopes.
Check the following boxes:
- View Channels
- Send Messages
- Read Message History
- Connect
- Speak

> 📸 SCREENSHOT 8
> What it should show: The Bot Permissions grid that appears below the Scopes section.
> It's a large grid of checkboxes organized into categories (General Permissions, Text
> Permissions, Voice Permissions). Show five checkboxes checked: "View Channels" under
> General, "Send Messages" and "Read Message History" under Text, and "Connect" and
> "Speak" under Voice. Draw a box or highlight around each of the five checked items.

**1.11** Scroll to the very bottom of the page. You'll see a box labeled **Generated URL**
with a long URL inside it and a **Copy** button.

**Copy this URL and save it** — this is your bot's invite link. You'll use it now to
add the bot to your server, and you'll need it again if you ever want to add it to
another server.

> 📸 SCREENSHOT 9
> What it should show: The bottom of the URL Generator page. There is a section called
> "Generated URL" with a long URL starting with "https://discord.com/api/oauth2/authorize?..."
> inside a text box, and a blue "Copy" button to the right of it.

**1.12** Open the copied URL in a new browser tab. A Discord authorization screen will appear.

> 📸 SCREENSHOT 10
> What it should show: The Discord OAuth authorization screen. It has your bot's name
> and icon at the top, then shows "Add to Server" with a dropdown to select which server,
> followed by a list of permissions the bot is requesting (the ones you checked in 1.10).
> At the bottom there are "Cancel" and "Authorize" buttons.

**1.13** Use the dropdown to select the server you want to add the bot to. Click **Authorize**,
then complete the CAPTCHA if one appears.

**1.14** You'll see a confirmation screen saying the bot was added. Open your Discord server —
the bot should now appear in the member list, shown as offline. It will go online in Step 5
when you start it.

> 📸 SCREENSHOT 11
> What it should show: The Discord success screen after authorization. It shows a green
> checkmark and text like "Authorized!" or "hedabot has been added to your server." This
> is shown in the browser, not inside Discord itself.

---

✅ **CALLOUT BOX — Green/Success**
Step 1 complete! Your bot exists and is in your server. It's offline for now — that's
expected. Move on to Step 2.

---
---

# Step 2 — Get a Deepgram API key

Deepgram is the service that converts speech to text. It's free to start — you get
$200 of credit when you sign up, which is a lot of transcription time.

**2.1** Go to console.deepgram.com and click **Sign Up**.

**2.2** Create an account with your email. No credit card required.

**2.3** After logging in, you'll land on the Deepgram Console dashboard. In the left
sidebar, click **API Keys**.

> 📸 SCREENSHOT 12
> What it should show: The Deepgram Console dashboard. The left sidebar shows navigation
> items. "API Keys" should be visible in the sidebar with an arrow or highlight pointing
> to it. The main area shows your account overview.

**2.4** Click **Create a New API Key**.

> 📸 SCREENSHOT 13
> What it should show: The API Keys page. There's a button labeled "Create a New API Key"
> or "+ New API Key" near the top of the page. If this is a new account, the key list
> below will be empty.

**2.5** Give it a name (e.g. "hedabot") and click **Create Key**.

**2.6** Your API key will appear on screen. **Copy it and save it** — Deepgram only shows
it once.

> 📸 SCREENSHOT 14
> What it should show: A modal or confirmation screen showing the newly created API key
> as a long string of characters. There's a copy button next to it. Note: blur or black
> out the actual key value in the screenshot.

---

⚠️ **CALLOUT BOX — Yellow/Warning**
Title: Save this key now
Like the Discord token, Deepgram only shows the full key once. Copy it to the same
safe place you put your Discord token.

---

✅ **CALLOUT BOX — Green/Success**
Step 2 complete! You have a Deepgram API key. Move on to Step 3.

---
---

# Step 3 — Set up Supabase

Supabase is where your transcripts get saved. You'll create a free database and run
one setup script to create the tables the bot needs.

**3.1** Go to supabase.com and click **Start your project**.

**3.2** Create an account (you can sign up with GitHub or email).

**3.3** Click **New Project**.

> 📸 SCREENSHOT 15
> What it should show: The Supabase dashboard after logging in. There's a green button
> labeled "New project" prominently displayed. If this is a new account, the projects
> list will be empty.

**3.4** Fill in the project details:
- **Name**: anything you want (e.g. "hedabot")
- **Database Password**: create a strong password and save it somewhere (you won't
  need it often but don't lose it)
- **Region**: pick the one closest to you

Click **Create new project**.

> 📸 SCREENSHOT 16
> What it should show: The "Create a new project" form. It has fields for Name,
> Database Password (with a "Generate a password" option), and Region (a dropdown).
> At the bottom is a "Create new project" button.

**3.5** Supabase will take about a minute to set up your project. You'll see a loading
screen. Wait for it to finish before continuing.

> 📸 SCREENSHOT 17
> What it should show: The project setup loading screen. It shows your project name
> with a spinner or progress indicator and text like "Setting up your project..." or
> "Provisioning your database."

**3.6** Once it's ready, you'll land on your project dashboard. In the left sidebar,
click **SQL Editor**.

> 📸 SCREENSHOT 18
> What it should show: The Supabase project dashboard. The left sidebar has icons and
> labels for different sections: Table Editor, SQL Editor, Database, Auth, Storage, etc.
> An arrow or highlight should point to "SQL Editor."

**3.7** Open the file `supabase/migrations/001_schema.sql` from the hedabot-oss folder
on your computer. Select all the text inside it (Ctrl+A / Cmd+A) and copy it.

**3.8** In the Supabase SQL Editor, click the editor area and paste the SQL you just copied
(Ctrl+V / Cmd+V). Then click the green **Run** button (or press Ctrl+Enter / Cmd+Enter).

> 📸 SCREENSHOT 19
> What it should show: The Supabase SQL Editor with the pasted SQL visible in the editor
> area. The SQL starts with "-- hedabot-oss schema" at the top. The green "Run" button
> is visible in the top right area of the editor. There should be a results panel at
> the bottom showing "Success. No rows returned."

**3.9** You should see **"Success. No rows returned."** in the results panel at the bottom.
That means the tables were created. If you see an error instead, paste the error message
into Claude or ChatGPT and ask what went wrong.

**3.10** Now get your credentials. In the left sidebar, click **Project Settings** (the
gear icon at the bottom), then click **API**.

> 📸 SCREENSHOT 20
> What it should show: The Supabase left sidebar with a gear icon at the bottom labeled
> "Project Settings." An arrow points to it. Alternatively, show the Settings page already
> open with "API" selected in the settings submenu.

**3.11** On the API settings page you'll find two things you need:

**Your Project URL** — it looks like `https://abcdefgh.supabase.co`. Copy it and save it.

**Your service_role key** — scroll down to the "Project API keys" section. You'll see
two keys: `anon` and `service_role`. Click **Reveal** next to `service_role`, then copy it.

> 📸 SCREENSHOT 21
> What it should show: The API settings page. At the top is the "Project URL" section
> showing a URL like "https://xxxxxxxxxxxx.supabase.co" with a copy button next to it.
> Lower down is the "Project API keys" section showing two rows: one labeled "anon" and
> one labeled "service_role". The service_role value is hidden (shown as bullet points)
> with a "Reveal" button. Draw two labeled boxes: one around the Project URL and one
> around the service_role row.

---

⚠️ **CALLOUT BOX — Yellow/Warning**
Title: Use the service_role key, not the anon key
There are two keys on that page. Make sure you copy the one labeled service_role.
The anon key is for apps that regular users access — it won't work for the bot.

---

✅ **CALLOUT BOX — Green/Success**
Step 3 complete! You now have your Supabase URL and service_role key saved. Move on
to Step 4.

---
---

# Step 4 — Set up your credentials file

You'll now put all four credentials you've collected into a single file.

**4.1** Inside the hedabot-oss folder on your computer, find the file called `.env.example`.

---

ℹ️ **CALLOUT BOX — Blue/Info**
Title: Can't see the file?
Files starting with a dot (.) are hidden by default on Mac and Windows.
On Mac: press Cmd+Shift+. in Finder to show hidden files.
On Windows: in File Explorer, click View → check "Hidden items."

---

**4.2** Make a copy of that file and rename the copy to `.env` (remove the word "example").

**4.3** Open `.env` in any text editor (Notepad on Windows, TextEdit on Mac, or anything else).
You'll see something like this:

```
DISCORD_TOKEN=
DEEPGRAM_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

**4.4** Paste your credentials after each `=` sign, with no spaces:

```
DISCORD_TOKEN=paste-your-discord-token-here
DEEPGRAM_API_KEY=paste-your-deepgram-key-here
SUPABASE_URL=paste-your-supabase-url-here
SUPABASE_SERVICE_ROLE_KEY=paste-your-service-role-key-here
```

**4.5** Save the file.

---

⚠️ **CALLOUT BOX — Yellow/Warning**
Title: Don't share this file
The .env file contains all your credentials in one place. Don't send it to anyone,
don't upload it to GitHub, and don't paste its contents in a public channel.

---

✅ **CALLOUT BOX — Green/Success**
Step 4 complete! All your credentials are in one place. One more step — deploying
the bot so it actually runs.

---
---

# Step 5 — Deploy the bot

There are two ways to run the bot. Pick the one that fits your situation:

| | **Fly.io (free)** | **Railway ($5/mo)** |
|---|---|---|
| Cost | Free forever | $5/month |
| Setup | Requires using a terminal | No terminal needed |
| Best for | Saving money | Easiest possible setup |

---

## Option A — Fly.io (free, uses a terminal)

**5A.1** Install the Fly.io command line tool by following the instructions at
fly.io/docs/hands-on/install-flyctl — pick the instructions for your operating
system (Mac, Windows, or Linux).

> 📸 SCREENSHOT 22
> What it should show: The Fly.io install page at fly.io/docs/hands-on/install-flyctl.
> It shows three tabs or sections for macOS, Linux, and Windows with a code snippet
> in each. The macOS section shows a `brew install flyctl` command. Draw an arrow to
> whichever tab matches the reader's operating system (or show all three).

**5A.2** Open a terminal on your computer.
- **Mac**: press Cmd+Space, type "Terminal", press Enter
- **Windows**: press the Windows key, type "Command Prompt", press Enter

**5A.3** Log in to Fly.io by typing this and pressing Enter:
```
fly auth login
```
A browser window will open asking you to log in or sign up for a Fly.io account.
Create a free account if you don't have one.

**5A.4** Navigate to the hedabot-oss folder in your terminal. If you're not sure how,
the easiest way is to type `cd ` (with a space after it), then drag the hedabot-oss
folder from your file manager into the terminal window. Press Enter.

**5A.5** Type this and press Enter:
```
fly launch
```
Fly.io will ask you a few questions. Answer them as follows:
- **"Would you like to copy its configuration to the new app?"** — Yes
- **"Choose an app name"** — press Enter to accept the default, or type a name
- **"Choose a region"** — pick the one closest to you
- **"Would you like to deploy now?"** — **No** (you need to add your credentials first)

> 📸 SCREENSHOT 23
> What it should show: A terminal window with the output of `fly launch`. Several
> questions are shown one by one with responses next to them. The last visible question
> is "Would you like to deploy now?" with the answer "No" typed or highlighted.

**5A.6** Now add your credentials by typing each of these lines, pressing Enter after each.
Replace the placeholder text with your actual values (no quotes needed):

```
fly secrets set DISCORD_TOKEN=your-discord-token-here
fly secrets set DEEPGRAM_API_KEY=your-deepgram-key-here
fly secrets set SUPABASE_URL=your-supabase-url-here
fly secrets set SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**5A.7** Deploy the bot:
```
fly deploy
```
This will take 2–4 minutes the first time. You'll see build output scrolling past.
When it's done you should see a line like **"✓ Machine e78 [app] update finished successfully"**
or similar.

> 📸 SCREENSHOT 24
> What it should show: A terminal window showing the tail end of `fly deploy` output.
> The last few lines show a success message. Look for green checkmarks or "finished
> successfully" text. The exact wording may vary by Fly.io version.

**5A.8** Check that the bot is running:
```
fly logs
```
Look for a line that says **"Bot ready"**. If you see it, the bot is online.

> 📸 SCREENSHOT 25
> What it should show: Terminal output from `fly logs`. Scrolling log output is visible
> with JSON-formatted lines. One of the lines contains "Bot ready" or similar. An arrow
> or highlight points to that specific line.

---

## Option B — Railway (no terminal needed)

**5B.1** Create a free account at railway.app.

**5B.2** Fork the hedabot-oss repo to your GitHub account by clicking the Fork button
at the top right of the GitHub page.

> 📸 SCREENSHOT 26
> What it should show: The hedabot-oss GitHub repository page. The top right area shows
> three buttons: Watch, Star, and Fork. An arrow points to the Fork button.

**5B.3** In Railway, click **New Project → Deploy from GitHub repo**. Select your
forked hedabot-oss repo.

> 📸 SCREENSHOT 27
> What it should show: The Railway "New Project" screen. It shows options including
> "Deploy from GitHub repo." An arrow points to that option.

**5B.4** Railway will detect the Dockerfile and start building. Click on the deployment
to open its settings, then click **Variables**.

**5B.5** Add each of your four credentials as a variable:

| Name | Value |
|------|-------|
| `DISCORD_TOKEN` | your Discord bot token |
| `DEEPGRAM_API_KEY` | your Deepgram API key |
| `SUPABASE_URL` | your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | your Supabase service_role key |

> 📸 SCREENSHOT 28
> What it should show: The Railway Variables panel for the deployment. It shows a list
> of environment variables with Name and Value columns. All four variables are listed
> with their names visible but values hidden (shown as ••••••). There's an "Add Variable"
> button at the top or bottom.

**5B.6** Railway will automatically redeploy after you add the variables. Watch the
deployment logs — when you see **"Bot ready"**, it's online.

---
---

# ✅ You're done — test it

**1.** Open your Discord server and join any voice channel.

**2.** In a text channel, type `/join` and press Enter.

> 📸 SCREENSHOT 29
> What it should show: A Discord server with a text channel open. The message input
> box at the bottom shows "/join" being typed, and a slash command autocomplete popup
> appears above it showing the "/join" command with the description "Join your voice
> channel and start recording." An arrow points to the autocomplete suggestion.

**3.** The bot should join your voice channel within a few seconds and reply:
*"Joined! Transcripts will appear here as people speak."*

**4.** Say something out loud. Within 1–2 seconds you should see a line appear in
the text channel like:

> 🎤 @YourName: what you just said

> 📸 SCREENSHOT 30
> What it should show: A Discord text channel with two messages visible. The first
> is the bot's "Joined!" confirmation message. The second is a transcript line showing
> the microphone emoji, a user mention (like @Username), a colon, and some spoken text.
> This is the "it's working" moment — make it feel celebratory in the doc.

**5.** Type `/leave` to stop.

---

🎉 **CALLOUT BOX — Green/Celebration**
Your bot is running! Everything said while it's in the channel is being transcribed
in real time and saved to your Supabase database. You can view the raw transcripts
any time in the Supabase dashboard under Table Editor → transcripts.

---
---

# Troubleshooting

**`/join` doesn't appear as a command when I type it**
Slash commands can take up to an hour to register after the bot first starts. If it's
been more than an hour, check that the bot is actually online (green dot in your server
member list) and that you invited it with the `applications.commands` scope in Step 1.

**The bot joins but nothing gets transcribed**
- Make sure the bot has permission to send messages in the text channel you used `/join` in
- Check your Deepgram API key is correct in your credentials
- Check the bot logs (fly logs or Railway dashboard) for any error messages

**"Missing required env vars" error in the logs**
One of your four credentials is missing or has a typo. Double-check each one.
Common mistake: copying extra spaces before or after the value.

**The bot disconnects unexpectedly**
On Fly.io, make sure your fly.toml has `min_machines_running = 1` and
`auto_stop_machines = "off"` — these are already set if you used this guide.

**I need to add the bot to another server**
Use the invite link you saved in Step 1.11. Open it in a browser and go through
the same Authorize flow, this time selecting the new server.

**I lost my credentials**
- Discord token: go back to the Developer Portal → your app → Bot → Reset Token
- Deepgram key: go to console.deepgram.com → API Keys → create a new one
- Supabase credentials: go to your project → Settings → API

---

*Made by [your name/org]. MIT license. Source code and issues at [GitHub link].*
