"""
Production-grade logging configuration
"""
# Standard library imports
import logging
import sys
from datetime import datetime

# Third-party imports
from fastapi import Request, Response
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured JSON logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  Defaults to INFO.

    Returns:
        Configured logger instance with JSON formatting.

    Example:
        >>> logger = setup_logging("DEBUG")
        >>> logger.info("Application started")
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    # JSON formatter for structured logs
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d", timestamp=True
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger


# Create logger instance
logger = setup_logging()


class RequestLogger:
    """Middleware for logging all API requests with structured JSON output."""

    @staticmethod
    async def log_request(request: Request, response: Response, process_time: float) -> None:
        """
        Log API request details in structured JSON format.

        Args:
            request: FastAPI Request object containing request details.
            response: FastAPI Response object containing response details.
            process_time: Time taken to process the request in seconds.

        Returns:
            None

        Note:
            Logs include: method, path, status code, processing time,
            client IP, and UTC timestamp.
        """
        logger.info(
            "API Request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "client_ip": request.client.host,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
