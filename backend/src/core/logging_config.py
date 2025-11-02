"""
Logging configuration for the application.

Provides custom formatter with request ID tracking and color-coded log levels.
"""
import logging
import sys
from src.core.config import get_settings
from src.core.middleware.request_id import get_request_id

settings = get_settings()
log_level = logging.DEBUG if settings.environment == "development" else logging.INFO


class RequestIDFormatter(logging.Formatter):
    """Custom formatter that handles request_id in log records with color coding."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'GRAY': '\033[90m'        # Gray for metadata
    }

    def format(self, record):
        request_id = getattr(record, 'request_id', 'N/A')
        
        # Shorten request ID for readability (first 8 chars)
        if request_id != 'N/A' and len(request_id) > 8:
            request_id = request_id[:8]
        
        record.request_id = request_id
        
        # Get color for log level
        level_name = record.levelname
        color = self.COLORS.get(level_name, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        gray = self.COLORS['GRAY']
        
        # Color the level name and add gray for metadata
        record.levelname = f"{color}{level_name:8}{reset}"
        record.name = f"{gray}{record.name}{reset}"
        record.request_id = f"{gray}{request_id}{reset}"
        
        return super().format(record)


def configure_logging():
    """
    Configure application logging with custom formatter and third-party log suppression.
    
    Sets up:
    - Custom RequestIDFormatter with color-coded log levels
    - Suppression of verbose third-party library logs
    - Uvicorn access log suppression (we log requests in middleware)
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RequestIDFormatter(
        '%(levelname)s | [%(name)s] [req=%(request_id)s] %(message)s'))
    logging.basicConfig(level=log_level, handlers=[handler])

    # Suppress Uvicorn access logs (we log requests in middleware)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Suppress verbose logs from all third-party libraries
    logging.getLogger("hpack").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http2").setLevel(logging.WARNING)
    logging.getLogger("hpack.table").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("supabase").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

