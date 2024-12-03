'''
AUTHOR : Aditya Bhatt 19:38PM 03-12-2024

NOTE:
1.This is just a high level file of practice and general testing/documentation

Use the Appropriate Log Level
DEBUG: Internal state details, variable values.
INFO: Normal operation logs like server starts, user actions.
WARNING: Something unexpected but not an error.
ERROR: Failures that might require investigation.
CRITICAL: System failures.
c. Avoid Over-Logging
Don't log sensitive information like passwords or API keys.
Avoid excessive logging, which can clutter your logs and slow down the application.
'''
import logging

logging.basicConfig(level=logging.DEBUG)  # Set the logging level
logging.debug("Debug message: for detailed diagnostic information")
logging.info("Info message: for general information")
logging.warning("Warning message: for non-critical issues")
logging.error("Error message: for serious issues")
logging.critical("Critical message: for very severe errors")
