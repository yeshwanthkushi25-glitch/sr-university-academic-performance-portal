"""
Backward-compatibility forwarder to app.db
"""

from app.db import get_db, init_db, seed_sample_data_if_empty

get_connection = get_db

__all__ = ["get_db", "get_connection", "init_db", "seed_sample_data_if_empty"]
