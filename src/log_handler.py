"""
In-memory log handler for capturing application logs.
"""
import logging
from collections import deque
from datetime import datetime
from typing import List, Dict
import re


class InMemoryLogHandler(logging.Handler):
    """
    Custom log handler that stores recent logs in memory.
    Uses a circular buffer (deque) with max size to prevent memory overflow.
    """

    def __init__(self, max_logs: int = 1000):
        """
        Initialize the handler.

        Args:
            max_logs: Maximum number of logs to keep in memory
        """
        super().__init__()
        self.logs = deque(maxlen=max_logs)
        self.lock = None  # Will be set by logging framework

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record by storing it in the deque.

        Args:
            record: Log record to store
        """
        try:
            # Skip SQLAlchemy and uvicorn logs (too verbose)
            if record.name.startswith(('sqlalchemy', 'uvicorn')):
                return

            # Format the log message
            msg = self.format(record)

            # Store log with metadata
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': msg,
                'event_id': self._extract_event_id(msg)
            }

            self.logs.append(log_entry)

        except Exception:
            self.handleError(record)

    def _extract_event_id(self, message: str) -> int | None:
        """
        Extract event ID from log message.

        Looks for patterns like "Event 1 #" or "Event {id} #"

        Args:
            message: Log message

        Returns:
            Event ID if found, None otherwise
        """
        # Match "Event 1 #" or "Event {id} #"
        match = re.search(r'Event (\d+) #', message)
        if match:
            return int(match.group(1))
        return None

    def get_logs(
        self,
        event_id: int = None,
        level: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get filtered logs.

        Args:
            event_id: Filter by event ID (from "Event {id} #" pattern)
            level: Filter by log level (INFO, WARNING, ERROR)
            limit: Maximum number of logs to return (most recent first)

        Returns:
            List of log entries
        """
        # Convert deque to list for filtering
        logs = list(self.logs)

        # Filter by event_id
        if event_id is not None:
            logs = [log for log in logs if log['event_id'] == event_id]

        # Filter by level
        if level:
            logs = [log for log in logs if log['level'] == level.upper()]

        # Return most recent logs first, limited
        return logs[-limit:]


# Global instance
_log_handler = InMemoryLogHandler(max_logs=2000)


def get_log_handler() -> InMemoryLogHandler:
    """
    Get the global log handler instance.

    Returns:
        InMemoryLogHandler instance
    """
    return _log_handler


def setup_logging():
    """
    Setup logging configuration with in-memory handler.
    Call this during application startup.
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Add our custom handler
    _log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    _log_handler.setFormatter(formatter)

    # Add to root logger
    root_logger.addHandler(_log_handler)

    # Also ensure our app loggers propagate
    app_logger = logging.getLogger('src')
    app_logger.setLevel(logging.INFO)
