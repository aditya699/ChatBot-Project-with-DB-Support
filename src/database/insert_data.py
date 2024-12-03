'''
Author - Aditya Bhatt 20:33 PM 03-12-2024

NOTE-
1.Faker is a Python library that helps generate fake but realistic-looking data for testing and development purposes. It's extremely useful when you need to populate databases with dummy data that looks authentic rather than just random strings or numbers.

BUG:
1.
'''

import pyodbc
import random
from datetime import datetime, timedelta
from faker import Faker
import logging
import os
from typing import Optional


def close_connection(connection: pyodbc.Connection) -> None:
        """
        Safely close the database connection.
        Args:
            connection: Active database connection
        """
        try:
            if connection:
                connection.close()
                logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")

# Initialize Faker
fake = Faker()
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
def create_database_connection() -> Optional[pyodbc.Connection]:
        """
        Create a connection to the database using Windows authentication.
        Returns: pyodbc.Connection object or None if connection fails
        """
        try:
            conn_str = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=DESKTOP-KLL45AE\\SQLEXPRESS;'
                'DATABASE=ADITYADB;'
                'Trusted_Connection=yes;'
            )
            
            connection = pyodbc.connect(conn_str)
            logger.info("Database connection established successfully")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return None
# Get logger instance
logger = logging.getLogger(__name__)
def insert_dummy_customers(connection: pyodbc.Connection, num_records: int = 100) -> bool:
    """
    Insert dummy customer records into the customers table
    """
    try:
        cursor = connection.cursor()
        
        for _ in range(num_records):
            email = fake.email()
            first_name = fake.first_name()
            last_name = fake.last_name()
            phone_number = fake.phone_number()[:20]  # Truncate to match varchar(20)
            
            cursor.execute("""
                INSERT INTO customers (email, first_name, last_name, phone_number)
                VALUES (?, ?, ?, ?)
            """, (email, first_name, last_name, phone_number))
        
        connection.commit()
        logger.info(f"Successfully inserted {num_records} customer records")
        return True
        
    except Exception as e:
        logger.error(f"Error inserting customer records: {str(e)}")
        connection.rollback()
        return False

def insert_dummy_tickets(connection: pyodbc.Connection, num_records: int = 100) -> bool:
    """
    Insert dummy support ticket records into the support_tickets table
    """
    try:
        cursor = connection.cursor()
        
        # Get all customer IDs
        cursor.execute("SELECT customer_id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
        
        # Possible values for categorical fields
        statuses = ['New', 'In Progress', 'Pending', 'Resolved', 'Closed']
        categories = ['Technical', 'Billing', 'Account', 'Product', 'General']
        
        for _ in range(num_records):
            customer_id = random.choice(customer_ids)
            subject = fake.sentence(nb_words=6)[:-1]  # Remove trailing period
            description = fake.paragraph()
            status = random.choice(statuses)
            category = random.choice(categories)
            rating = random.randint(1, 5) if random.random() > 0.3 else None
            
            # Generate random dates
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            resolved_at = None
            if status in ['Resolved', 'Closed']:
                resolved_at = created_at + timedelta(days=random.randint(1, 30))
            
            cursor.execute("""
                INSERT INTO support_tickets 
                (customer_id, subject, description, status, category, rating, created_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, subject, description, status, category, rating, created_at, resolved_at))
        
        connection.commit()
        logger.info(f"Successfully inserted {num_records} support ticket records")
        return True
        
    except Exception as e:
        logger.error(f"Error inserting support ticket records: {str(e)}")
        connection.rollback()
        return False

if __name__ == "__main__":
    # Create database connection
    conn = create_database_connection()
    
    if conn:
        # Insert dummy data
        if insert_dummy_customers(conn):
            insert_dummy_tickets(conn)
        
        # Close connection
        close_connection(conn)