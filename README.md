# K SCRIPT TOOL

A Python-based Telegram group management utility designed for Android Termux.

- **Developer:** KEE
- **Platform:** Android / Termux
- **Python:** 3.10+
- **Telegram client:** Telethon
- **Repository:** Private

## Current status

Phase 2 adds interactive Telegram account authentication with OTP and optional two-step verification (2FA). Phase 3 adds authorized member scraping and local SQLite storage. Phase 4 adds CSV import/export for locally stored member records. Phase 5 adds public-group joining via Telegram's normal join request, private invite-link importing, and authorized invite-link creation. Phase 6 adds a sanitized local activity history for CSV import/export, member scraping, and group join/invite operations, plus a summary report. Phase 7 audit updates stream report summaries to keep memory use bounded and add validation tests.

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

Choose **[1] Telegram account setup**. Enter your phone number in international format, then the Telegram verification code. If two-step verification is enabled, enter its password when prompted; password input is hidden. Use **[6] Account management** to view the logged-in profile (user ID, name, username, and a masked phone number) or to log out after confirming. Logout uses Telegram's session logout operation; choosing no/cancel leaves the session active. After login, choose **[3] Member-list tools**, enter a group username or ID that the account can access, and optionally set a positive member limit. Records are stored locally in `data/members.sqlite3` and deduplicated by Telegram user ID. Press Ctrl+C to stop; records saved so far are retained.

Choose **[2] Import / export member list** to export all stored records to a CSV file or import a CSV file. Exports use UTF-8 with BOM for spreadsheet compatibility. Imports accept UTF-8/UTF-8-BOM, require a `user_id` column, skip invalid rows, and deduplicate repeated IDs (the last valid row wins). Existing records with the same user ID are updated. Review the file path and confirm before importing. CSV files may contain personal member data; keep them local and never commit them to GitHub.

Choose **[4] Invitation management** to join public groups by username or private groups using a valid invite link, or create an invite link for groups you administer. Join and invite operations respect Telegram permissions and FloodWait responses; invite links are only created when your account has the required admin rights. Direct member-add workflows are not enabled in this phase.

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
├── modules/           # Scraper, storage, CSV import/export, invitations, reports
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
