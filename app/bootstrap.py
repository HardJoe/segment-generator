"""Command-line entry point for database setup before the API starts."""

from app.database import bootstrap_database


def main() -> None:
    bootstrap_database()


if __name__ == "__main__":
    main()
