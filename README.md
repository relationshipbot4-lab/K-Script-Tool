# K SCRIPT TOOL

A Python-based Telegram group management utility designed for Android Termux.

- **Developer:** KEE
- **Platform:** Android / Termux
- **Python:** 3.10+
- **Telegram client:** Telethon
- **Repository:** Private

## Current status

Phases 2–7 delivered the initial authentication, authorized member scraping/local storage, CSV import/export, group join/invite workflows, activity reporting, and report-streaming audit. Phase 8 adds terminal clearing/redraw on startup and menu return. Phase 9 adds account profile viewing, masked phone display, and confirmed logout. Phase 10 hardens best-effort cleanup after connection failures. Phase 11 fixes scrape progress to count every scanned member, including skipped records. Phase 12 adds CSV export destination-path regression coverage. Phase 13 adds invite-link workflow regression tests. Phase 14 validates and normalizes report timestamps to UTC on read. Phase 15 centralizes Telegram client connection/disconnect lifecycle handling. Phase 16 documents CSV spreadsheet formula risks and checks repository secret/data ignore rules. Phase 17 expands main-menu navigation tests. Phase 18 is the final CI/documentation release gate.

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

Choose **[2] Import / export member list** to export all stored records to a CSV file or import a CSV file. Exports use UTF-8 with BOM for spreadsheet compatibility. Imports accept UTF-8/UTF-8-BOM, require a `user_id` column, skip invalid rows, and deduplicate repeated IDs (the last valid row wins). Existing records with the same user ID are updated. Review the file path and confirm before importing. CSV files may contain personal member data; keep them local and never commit them to GitHub. Treat profile-derived CSV cells as untrusted text: spreadsheet software may interpret formula-like values as executable formulas. This export does not neutralize spreadsheet formulas, so inspect files as plain text or use a trusted sanitization workflow before opening them in a spreadsheet.

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

## Release gate

Before running on a real Termux device:

1. Run the full test suite: `python -m unittest discover -s tests -v`.
2. Compile-check the project: `python -m compileall -q .`.
3. Configure credentials only in your local `.env` file.
4. Verify `.env`, Telegram session files, local databases, CSV exports, and logs remain untracked.
5. Test account login/profile/logout on the user's device and verify Telegram session state after logout.
6. Verify authorized group scraping, CSV import/export, group join/invite behavior, FloodWait handling, and terminal redraw on Termux using only accounts/groups the user is authorized to manage.

**Device validation is still required.** GitHub Actions passing does not substitute for testing Telegram RPC behavior or terminal UX on a real Android/Termux environment. This repository does not implement a direct member-add workflow; `modules/adder.py` remains a placeholder.
