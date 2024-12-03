'''
NOTE : No need to see the file this is file just for testing stuff 

'''
import logging
from datetime import datetime
import os

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create a unique log filename with timestamp
log_filename = f'logs/error_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Keep console logging if you want both
    ]
)

# Get logger instance
logger = logging.getLogger(__name__)

# Example usage
try:
    # Your database code here
    pass
except Exception as e:
    logger.error(f"Database error occurred: {str(e)}")
finally:
    logger.info("Database connection closed successfully")