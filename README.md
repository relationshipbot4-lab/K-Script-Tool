# K SCRIPT TOOL

A Python-based Telegram group management utility designed for Android Termux.

- **Developer:** KEE
- **Platform:** Android / Termux
- **Python:** 3.10+
- **Telegram client:** Telethon
- **Repository:** Private

## Current status

This repository contains the initial project foundation. Telegram account login, member-list import/export, reporting, and consent-based invitation workflows will be implemented and tested incrementally.

The tool is intended for groups you own or are authorized to manage. It must respect Telegram permissions, user privacy settings, rate limits, and anti-spam protections. It does not bypass invite restrictions or attempt to evade FloodWait limits.

## Termux setup

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/relationshipbot4-lab/K-Script-Tool.git
cd K-Script-Tool
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your own Telegram API credentials from https://my.telegram.org.

Run:

```bash
python main.py
```

## Security

- Never commit `.env`, Telegram session files, API credentials, exported member data, or logs.
- Keep the repository private, but do not treat repository privacy as a substitute for secret management.
- If a credential is exposed, revoke or rotate it immediately.
- Use Telegram account data only where you have a legitimate purpose and authorization.

## Project layout

```text
K-Script-Tool/
├── core/          # Telegram client and session management
├── modules/       # Scraper, import/export, invitations, reports
├── data/          # Local data (ignored by Git)
├── sessions/      # Telegram sessions (ignored by Git)
├── logs/          # Local logs (ignored by Git)
├── config.py
├── main.py
├── requirements.txt
└── .env.example
```

## Development

Features are being added in small, reviewable stages. Existing behavior and public function names should be preserved when extending the project.
