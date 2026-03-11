import mysql.connector
from mysql.connector import MySQLConnection

from config import Config


def get_connection() -> MySQLConnection:
    """
    Create and return a new MySQL connection using environment variables.

    Expected env vars (via Config):
    - DB_HOST
    - DB_PORT
    - DB_USER
    - DB_PASSWORD
    - DB_NAME
    """
    return mysql.connector.connect(
        host=Config.DB_HOST or "localhost",
        port=int(Config.DB_PORT or 3306),
        user=Config.DB_USER or "root",
        password=Config.DB_PASSWORD or "",
        database=Config.DB_NAME or "project_allocator",
    )


def init_db() -> None:
    """
    Ensure required tables exist: users, projects.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(64) PRIMARY KEY,
            entity_type VARCHAR(32),
            role VARCHAR(255),
            seniority VARCHAR(255),
            total_experience_years INT,
            primary_skills TEXT,
            secondary_skills TEXT,
            domains TEXT,
            summary TEXT,
            file_link TEXT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id VARCHAR(64) PRIMARY KEY,
            entity_type VARCHAR(32),
            required_role VARCHAR(255),
            required_seniority VARCHAR(255),
            required_experience_years INT,
            required_skills TEXT,
            optional_skills TEXT,
            required_domains TEXT,
            summary TEXT,
            file_link TEXT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


# Initialize tables on import so the rest of the app can assume they exist.
init_db()

