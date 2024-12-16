import sqlite3
from cryptography.fernet import Fernet
import os
import cryptography
import pandas as pd
from datetime import datetime


# Load or generate a key for encryption
key_file = "Team Directory/Mc and John Christian/db/secret.key"
if os.path.exists(key_file):
    with open(key_file, "rb") as file:
        key = file.read()
else:
    key = Fernet.generate_key()
    with open(key_file, "wb") as file:
        file.write(key)

cipher_suite = Fernet(key)


def init_db():
    conn = sqlite3.connect("Team Directory/Mc and John Christian/db/jira_lite.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, connection_string TEXT, container_name TEXT)"""
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS merged_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        TaskID TEXT,
        TaskName TEXT,
        Description TEXT,
        Status TEXT,
        "AssigneeName-Role" TEXT,
        DueDate TEXT,
        Priority TEXT,
        SprintName TEXT,
        SprintGoal TEXT,
        version,
        created_at
    )
    """
    )
    conn.commit()
    return conn, c


def get_config(c):
    c.execute("SELECT connection_string, container_name FROM config WHERE id=1")
    config = c.fetchone()
    if config:
        try:
            connection_string = cipher_suite.decrypt(config[0].encode()).decode()
        except cryptography.fernet.InvalidToken:
            return None
        container_name = config[1]
        return connection_string, container_name
    return None


def save_config(c, conn, connection_string, container_name):
    encrypted_connection_string = cipher_suite.encrypt(
        connection_string.encode()
    ).decode()
    c.execute("DELETE FROM config WHERE id=1")
    c.execute(
        "INSERT INTO config (id, connection_string, container_name) VALUES (1, ?, ?)",
        (encrypted_connection_string, container_name),
    )
    conn.commit()


def save_merged_data_to_db(cursor, merged_data: pd.DataFrame, version: int):
    merged_data["version"] = version
    merged_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    merged_data.to_sql(
        "merged_data", cursor.connection, if_exists="append", index=False
    )


def get_latest_version(c):
    c.execute("SELECT MAX(version) FROM merged_data")
    latest_version = c.fetchone()[0]
    return latest_version if latest_version else 1
