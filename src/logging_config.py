"""
Structured logging configuration for the analysis service.
Provides JSON-formatted logs with context and correlation tracking.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import traceback


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format with additional context.
    """

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

        # Add custom fields if they exist
        if hasattr(record, 'job_id'):
            log_data['job_id'] = record.job_id
        if hasattr(record, 'company_name'):
            log_data['company_name'] = record.company_name
        if hasattr(record, 'step'):
            log_data['step'] = record.step
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'api_name'):
            log_data['api_name'] = record.api_name
        if hasattr(record, 'response_size'):
            log_data['response_size'] = record.response_size
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': ''.join(traceback.format_exception(*record.exc_info))
            }

        return json.dumps(log_data)


class ContextLogger:
    """
    Logger wrapper that adds context to all log messages.
    """

    def __init__(self, logger: logging.Logger, context: Dict[str, Any] = None):
        self.logger = logger
        self.context = context or {}

    def _log(self, level: int, message: str, extra: Dict[str, Any] = None):
        """Internal method to log with context."""
        log_extra = {**self.context}
        if extra:
            log_extra.update(extra)
        self.logger.log(level, message, extra=log_extra)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        if exc_info:
            self.logger.error(message, exc_info=True, extra={**self.context, **kwargs})
        else:
            self._log(logging.ERROR, message, kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        if exc_info:
            self.logger.critical(message, exc_info=True, extra={**self.context, **kwargs})
        else:
            self._log(logging.CRITICAL, message, kwargs)

    def with_context(self, **kwargs) -> 'ContextLogger':
        """Create a new logger with additional context."""
        new_context = {**self.context, **kwargs}
        return ContextLogger(self.logger, new_context)


def setup_logging(
    log_level: str = "INFO",
    use_json: bool = True,
    log_file: str = None
) -> logging.Logger:
    """
    Set up structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (True) or plain text (False)
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("analysis_service")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if use_json:
        console_handler.setFormatter(StructuredFormatter())
    else:
        # Fallback to standard formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        if use_json:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_context_logger(job_id: str = None, company_name: str = None, **kwargs) -> ContextLogger:
    """
    Get a context logger with pre-filled context fields.

    Args:
        job_id: Job ID for tracking
        company_name: Company name being analyzed
        **kwargs: Additional context fields

    Returns:
        ContextLogger instance with context
    """
    logger = logging.getLogger("analysis_service")
    context = {}

    if job_id:
        context['job_id'] = job_id
    if company_name:
        context['company_name'] = company_name
    if kwargs:
        context.update(kwargs)

    return ContextLogger(logger, context)
