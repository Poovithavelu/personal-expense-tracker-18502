import logging
from typing import Optional, Any, Dict, Iterable
import threading
from mysql.connector import pooling, Error as MySQLError
from .config import get_mysql_config

_logger = logging.getLogger(__name__)


class _DBPool:
    """Internal singleton wrapper for MySQL connection pooling."""
    _instance_lock = threading.Lock()
    _pool: Optional[pooling.MySQLConnectionPool] = None

    @classmethod
    def get_pool(cls) -> pooling.MySQLConnectionPool:
        if cls._pool is not None:
            return cls._pool

        with cls._instance_lock:
            if cls._pool is None:
                cfg = get_mysql_config()
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="expense_tracker_pool",
                    pool_size=10,
                    pool_reset_session=True,
                    host=cfg.host,
                    user=cfg.user,
                    password=cfg.password,
                    database=cfg.database,
                    port=cfg.port,
                    autocommit=False,
                )
                _logger.info("Initialized MySQL connection pool")
        return cls._pool


# PUBLIC_INTERFACE
def get_connection():
    """Acquire a connection from the pool."""
    return _DBPool.get_pool().get_connection()


# PUBLIC_INTERFACE
def init_schema() -> None:
    """Initialize database schema if not exists for categories and expenses."""
    ddl_statements: Iterable[str] = [
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount DECIMAL(10,2) NOT NULL,
            category_id INT,
            description VARCHAR(255),
            expense_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_expenses_category
                FOREIGN KEY (category_id) REFERENCES categories(id)
                ON UPDATE CASCADE ON DELETE SET NULL,
            INDEX (expense_date),
            INDEX (category_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    ]
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        for ddl in ddl_statements:
            cur.execute(ddl)
        conn.commit()
        cur.close()
        _logger.info("Database schema ensured")
    except MySQLError:
        _logger.exception("Failed to initialize schema")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


# PUBLIC_INTERFACE
def query(sql: str, params: Optional[Iterable[Any]] = None) -> list[Dict[str, Any]]:
    """Execute a SELECT query and return list of dict rows."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return rows
    except MySQLError:
        _logger.exception("Query failed")
        raise
    finally:
        if conn:
            conn.close()


# PUBLIC_INTERFACE
def execute(sql: str, params: Optional[Iterable[Any]] = None) -> int:
    """Execute an INSERT/UPDATE/DELETE and return lastrowid if applicable, else affected count."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        last_id = cur.lastrowid
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return last_id if last_id not in (None, 0) else affected
    except MySQLError:
        if conn:
            conn.rollback()
        _logger.exception("Execute failed")
        raise
    finally:
        if conn:
            conn.close()
