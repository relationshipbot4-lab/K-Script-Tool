"""Entry point for K SCRIPT TOOL."""

from config import DEVELOPER_NAME, TOOL_NAME
from core.auth import authenticate_telegram_account
from modules.csv_manager import run_csv_menu
from modules.scraper import run_scraper_menu
from modules.invite import run_invite_menu


def show_banner() -> None:
    print("\033[96m")
    print("╔══════════════════════════════════════╗")
    print(f"║ {TOOL_NAME:^36} ║")
    print("║       TELEGRAM GROUP MANAGER         ║")
    print("╠══════════════════════════════════════╣")
    print(f"║ Developer: {DEVELOPER_NAME:<26} ║")
    print("╚══════════════════════════════════════╝")
    print("\033[0m")


def show_menu() -> None:
    print("\n[1] Telegram account setup")
    print("[2] Import / export member list")
    print("[3] Member-list tools")
    print("[4] Invitation management")
    print("[5] Activity report")
    print("[0] Exit")


def main() -> None:
    show_banner()
    while True:
        show_menu()
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        if choice == "1":
            authenticate_telegram_account()
        elif choice == "2":
            run_csv_menu()
        elif choice == "3":
            run_scraper_menu()
        elif choice == "4":
            run_invite_menu()
        elif choice == "5":
            print("This module is scheduled for a later development phase.")
        else:
            print("Invalid option. Please choose 0-5.")


if __name__ == "__main__":
    main()
