# K SCRIPT TOOL

A Python-based Telegram group management utility designed for Android Termux.

- **Developer:** KEE
- **Platform:** Android / Termux
- **Python:** 3.10+
- **Telegram client:** Telethon
- **Repository:** Private

## Current status

Phase 2 adds interactive Telegram account authentication with OTP and optional two-step verification (2FA). Phase 3 adds authorized member scraping and local SQLite storage. CSV import/export, reporting, and invitation workflows are planned for later phases.

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

Edit `.env` and set the exact variable names below using your own Telegram API credentials from https://my.telegram.org:

```dotenv
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
```

Do not rename these variables to `API_ID` or `API_HASH`; the application reads `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`.

Run:

```bash
python main.py
```

Choose **[1] Telegram account setup**. Enter your phone number in international format, then the Telegram verification code. If two-step verification is enabled, enter its password when prompted; password input is hidden. After login, choose **[3] Member-list tools**, enter a group username or ID that the account can access, and optionally set a positive member limit. Records are stored locally in `data/members.sqlite3` and deduplicated by Telegram user ID. Press Ctrl+C to stop; records saved so far are retained.

The authentication flow uses Telethon's synchronous client interface because the command-line menu and login handler are synchronous. The Telethon session is stored locally under `sessions/`. Never share or upload it to GitHub. To sign out, use Telegram's active-session settings or remove the local session files after closing the tool.

## Security

- Never commit `.env`, Telegram session files, API credentials, exported member data, or logs.
- Keep the repository private, but do not treat repository privacy as a substitute for secret management.
- OTP and 2FA passwords are runtime-only inputs and are not saved by this application.
- If a credential is exposed, revoke or rotate it immediately.
- Use Telegram account data only where you have a legitimate purpose and authorization.

## Project layout

```text
K-Script-Tool/
├── .github/workflows/ # Automated tests
├── core/              # Telegram client and authentication
├── modules/           # Authorized scraper, local storage, import/export, invitations, reports
├── tests/             # Unit tests
├── data/              # Local data (ignored by Git)
├── sessions/          # Telegram sessions (ignored by Git)
├── logs/              # Local data (ignored by Git)
├── config.py
├── main.py
└── requirements.txt
```

## Development

Features are added in small, reviewable stages. Existing behavior and public function names should be preserved when extending the project.
