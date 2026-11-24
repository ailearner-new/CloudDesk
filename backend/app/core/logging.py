"""JSON logging configuration for CloudDesk Support Platform."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

# Context variables for request-scoped logging
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
workflow_id_var: ContextVar[Optional[str]] = ContextVar("workflow_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON log formatter with request_id and workflow_id context."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request_id and workflow_id if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        workflow_id = workflow_id_var.get()
        if workflow_id:
            log_data["workflow_id"] = workflow_id

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "msg", "name", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info", "exc_text",
                "stack_info", "getMessage"
            }:
                # Skip private attributes
                if not key.startswith("_"):
                    # Redact sensitive data
                    if key in ("password", "secret", "token", "api_key", "authorization"):
                        log_data[key] = "***REDACTED***"
                    else:
                        log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers = [handler]

    # Reduce noise from third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def log_context(request_id: Optional[str] = None, workflow_id: Optional[str] = None):
    """Context manager to bind request_id and workflow_id to log context."""
    class LogContext:
        def __init__(self, req_id: Optional[str], wf_id: Optional[str]):
            self.request_id_token = None
            self.workflow_id_token = None
            self.req_id = req_id
            self.wf_id = wf_id

        def __enter__(self):
            if self.req_id:
                self.request_id_token = request_id_var.set(self.req_id)
            if self.wf_id:
                self.workflow_id_token = workflow_id_var.set(self.wf_id)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.request_id_token:
                request_id_var.reset(self.request_id_token)
            if self.workflow_id_token:
                workflow_id_var.reset(self.workflow_id_token)

    return LogContext(request_id, workflow_id)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)