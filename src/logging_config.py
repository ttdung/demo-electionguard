"""Structured logging configuration for ElectionGuard operations."""
import logging
import json
from datetime import datetime
from typing import Any
from src.log_handler import get_log_handler


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO"):
    """Configure structured logging for the application."""
    # Create formatter
    formatter = JSONFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Add in-memory log handler for log viewer
    memory_handler = get_log_handler()
    memory_handler.setLevel(logging.INFO)
    simple_formatter = logging.Formatter('%(message)s')
    memory_handler.setFormatter(simple_formatter)
    root_logger.addHandler(memory_handler)

    # Set specific levels for libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def log_electionguard_operation(
    logger: logging.Logger,
    operation: str,
    event_id: str | None = None,
    customer_id: str | None = None,
    details: dict[str, Any] | None = None,
):
    """
    Log ElectionGuard operations with structured data.

    Args:
        logger: Logger instance
        operation: Operation name (e.g., "ballot_encryption", "tally_ceremony")
        event_id: Vote event ID if applicable
        customer_id: Customer ID if applicable
        details: Additional operation details
    """
    log_data = {
        "operation": operation,
        "event_id": event_id,
        "customer_id": customer_id,
        "details": details or {},
    }

    # Add extra_data attribute to record
    extra = {"extra_data": log_data}
    logger.info(f"ElectionGuard operation: {operation}", extra=extra)
