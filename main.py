"""Entry point for K SCRIPT TOOL."""

from config import DEVELOPER_NAME, TOOL_NAME


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
        if choice in {"1", "2", "3", "4", "5"}:
            print("This module is scheduled for the next development phase.")
        else:
            print("Invalid option. Please choose 0-5.")


if __name__ == "__main__":
    main()
