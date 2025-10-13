import logging
import bpy
import os

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(os.path.expanduser('~/open_video_tracker_importer.log'))

# Set levels for handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_info(message, op=None):
    """Log an info message."""
    logger.info(message)
    if op:
        op.report({'INFO'}, message)

def log_warning(message, op=None):
    """Log a warning message."""
    logger.warning(message)
    if op:
        op.report({'WARNING'}, message)

def log_error(message, op=None):
    """Log an error message."""
    logger.error(message)
    if op:
        op.report({'ERROR'}, message)

def log_debug(message, op=None):
    """Log a debug message."""
    logger.debug(message)
