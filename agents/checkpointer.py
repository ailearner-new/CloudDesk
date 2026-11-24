"""Checkpointer for CloudDesk Support Platform workflow."""

import os
from typing import Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.core.config import get_settings


_checkpointer = None


def get_checkpointer():
    """Get or create the checkpointer."""
    global _checkpointer
    if _checkpointer is None:
        settings = get_settings()
        checkpoint_path = settings.CHECKPOINT_DB_PATH

        if checkpoint_path == ":memory:":
            _checkpointer = InMemorySaver()
        else:
            # Ensure directory exists
            os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
            _checkpointer = AsyncSqliteSaver.from_conn_string(checkpoint_path)

    return _checkpointer