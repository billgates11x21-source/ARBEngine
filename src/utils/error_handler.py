import logging
import traceback
import time
import threading
import json
import os
from typing import Dict, List, Callable, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("error_logs.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ARBEngine")

class ErrorHandler:
    """
    Centralized error handling system for ARBEngine
    
    Features:
    - Error logging with context
    - Automatic retry mechanism
    - Error notification
    - Recovery strategies
    """
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: Dict[str, List[float]] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.notification_callbacks: List[Callable] = []
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.error_threshold = 5  # errors in timeframe
        self.error_timeframe = 300  # 5 minutes
        
    def register_recovery_strategy(self, error_type: str, strategy: Callable) -> None:
        """Register a recovery strategy for a specific error type"""
        self.recovery_strategies[error_type] = strategy
        
    def register_notification_callback(self, callback: Callable) -> None:
        """Register a notification callback"""
        self.notification_callbacks.append(callback)
        
    def handle_error(self, error: Exception, context: str, retry_func: Optional[Callable] = None, 
                    retry_args: tuple = (), retry_kwargs: Dict[str, Any] = {}) -> Any:
        """
        Handle an error with context
        
        Args:
            error: The exception that was raised
            context: Description of where the error occurred
            retry_func: Function to retry if applicable
            retry_args: Arguments for retry_func
            retry_kwargs: Keyword arguments for retry_func
            
        Returns:
            Result of retry_func if successful, None otherwise
        """
        error_type = type(error).__name__
        error_key = f"{context}:{error_type}"
        
        # Log the error
        logger.error(f"Error in {context}: {error}")
        logger.error(traceback.format_exc())
        
        # Update error counts
        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0
            self.error_timestamps[error_key] = []
        
        self.error_counts[error_key] += 1
        self.error_timestamps[error_key].append(time.time())
        
        # Clean up old timestamps
        current_time = time.time()
        self.error_timestamps[error_key] = [
            ts for ts in self.error_timestamps[error_key] 
            if current_time - ts < self.error_timeframe
        ]
        
        # Check if we're seeing too many errors
        if len(self.error_timestamps[error_key]) >= self.error_threshold:
            self._handle_threshold_exceeded(error_key, error, context)
        
        # Try recovery strategy if available
        if error_type in self.recovery_strategies:
            try:
                logger.info(f"Attempting recovery strategy for {error_type}")
                self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed: {recovery_error}")
        
        # Retry if function provided
        if retry_func:
            return self._retry_operation(retry_func, retry_args, retry_kwargs, error_key)
        
        return None
    
    def _retry_operation(self, func: Callable, args: tuple, kwargs: Dict[str, Any], error_key: str) -> Any:
        """Retry an operation with exponential backoff"""
        retries = 0
        while retries < self.max_retries:
            try:
                logger.info(f"Retry attempt {retries + 1} for {error_key}")
                time.sleep(self.retry_delay * (2 ** retries))  # Exponential backoff
                result = func(*args, **kwargs)
                logger.info(f"Retry successful for {error_key}")
                return result
            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
                retries += 1
        
        logger.error(f"All {self.max_retries} retry attempts failed for {error_key}")
        self._send_notifications(f"Operation failed after {self.max_retries} retries: {error_key}")
        return None
    
    def _handle_threshold_exceeded(self, error_key: str, error: Exception, context: str) -> None:
        """Handle case where error threshold is exceeded"""
        message = f"Error threshold exceeded for {error_key}. {len(self.error_timestamps[error_key])} errors in the last {self.error_timeframe} seconds."
        logger.critical(message)
        
        # Send notifications
        self._send_notifications(message)
        
        # Save error details to file for analysis
        self._save_error_report(error_key, error, context)
    
    def _send_notifications(self, message: str) -> None:
        """Send notifications through all registered callbacks"""
        for callback in self.notification_callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
    
    def _save_error_report(self, error_key: str, error: Exception, context: str) -> None:
        """Save detailed error report to file"""
        try:
            os.makedirs("error_reports", exist_ok=True)
            filename = f"error_reports/error_{int(time.time())}_{error_key.replace(':', '_')}.json"
            
            report = {
                "error_key": error_key,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": time.time(),
                "traceback": traceback.format_exc(),
                "occurrence_count": self.error_counts.get(error_key, 0),
                "recent_occurrences": len(self.error_timestamps.get(error_key, []))
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Error report saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save error report: {e}")

# Create a global instance
error_handler = ErrorHandler()

def handle_errors(context: str):
    """
    Decorator for functions to automatically handle errors
    
    Args:
        context: Description of the function's context
        
    Example:
        @handle_errors("fetch_market_data")
        def fetch_market_data():
            # function code
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_error(
                    e, context, func, args, kwargs
                )
        return wrapper
    return decorator