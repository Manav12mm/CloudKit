"""Database Connection Manager providing unified SQLAlchemy engine for SQLite & MySQL."""

import logging
from typing import Dict, Any
from sqlalchemy import create_engine, Engine
import config

logger = logging.getLogger(__name__)

_ENGINE_CACHE: Dict[str, Engine] = {}

def get_db_engine(engine_type: str = None) -> Engine:
    """Return a cached SQLAlchemy Engine instance.
    
    Args:
        engine_type: 'sqlite' or 'mysql'. Defaults to config.DB_ENGINE_TYPE.
    """
    engine_type = (engine_type or config.DB_ENGINE_TYPE).lower()
    
    if engine_type in _ENGINE_CACHE:
        return _ENGINE_CACHE[engine_type]

    if engine_type == "sqlite":
        db_path = config.SQLITE_DB_PATH
        connection_str = f"sqlite:///{db_path}"
        logger.info(f"Initializing SQLite engine at {db_path}")
        engine = create_engine(connection_str, echo=False)
    elif engine_type == "mysql":
        connection_str = (
            f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
            f"@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}"
        )
        logger.info(f"Initializing MySQL engine at {config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}")
        engine = create_engine(connection_str, echo=False, pool_pre_ping=True)
    else:
        raise ValueError(f"Unsupported database engine type: {engine_type}")

    _ENGINE_CACHE[engine_type] = engine
    return engine

def set_custom_sqlite_path(db_path: str) -> Engine:
    """Dynamically set and return SQLite engine for a custom database file."""
    connection_str = f"sqlite:///{db_path}"
    logger.info(f"Setting custom SQLite engine at {db_path}")
    engine = create_engine(connection_str, echo=False)
    _ENGINE_CACHE["sqlite"] = engine
    _ENGINE_CACHE["custom"] = engine
    return engine

def set_custom_mysql_config(host: str, port: int, user: str, password: str, database: str) -> Engine:
    """Dynamically set and return MySQL engine for custom database credentials."""
    connection_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    logger.info(f"Setting custom MySQL engine at {host}:{port}/{database}")
    engine = create_engine(connection_str, echo=False, pool_pre_ping=True)
    _ENGINE_CACHE["mysql"] = engine
    _ENGINE_CACHE["custom"] = engine
    return engine

def get_db_connection(engine_type: str = None):
    """Context manager for obtaining a raw database connection."""
    engine = get_db_engine(engine_type)
    return engine.connect()

def get_dialect_name(engine_type: str = None) -> str:
    """Return the dialect name ('sqlite' or 'mysql')."""
    engine_type = (engine_type or config.DB_ENGINE_TYPE).lower()
    return engine_type
