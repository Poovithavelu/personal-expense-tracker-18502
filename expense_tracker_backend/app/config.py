import os
from dataclasses import dataclass


@dataclass
class MySQLConfig:
    """Holds MySQL configuration values loaded from environment variables."""
    host: str
    user: str
    password: str
    database: str
    port: int


# PUBLIC_INTERFACE
def get_mysql_config() -> MySQLConfig:
    """Return MySQLConfig built from environment variables.

    Required env vars (must be provided by deployment/orchestrator):
    - MYSQL_URL: Hostname or IP of the MySQL server
    - MYSQL_USER: Username
    - MYSQL_PASSWORD: Password
    - MYSQL_DB: Database name
    - MYSQL_PORT: Port number (int)
    """
    host = os.getenv("MYSQL_URL", "")
    user = os.getenv("MYSQL_USER", "")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "")
    port = int(os.getenv("MYSQL_PORT", "3306"))

    return MySQLConfig(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
    )
