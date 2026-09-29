from app.database.db import initialize_database


if __name__ == "__main__":
    initialize_database()
    print("Database initialized with 75 mock orders.")
