"""
Production-grade logging configuration
"""
import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO"):
    """Configure structured JSON logging"""
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # JSON formatter for structured logs
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d',
        timestamp=True
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    
    return logger


# Create logger instance
logger = setup_logging()


class RequestLogger:
    """Middleware for logging all API requests"""
    
    @staticmethod
    async def log_request(request, response, process_time: float):
        """Log API request details"""
        logger.info(
            "API Request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "client_ip": request.client.host,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

