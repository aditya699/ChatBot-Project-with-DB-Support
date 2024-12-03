import pyodbc
import logging
from typing import Optional
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

def create_tables(connection: pyodbc.Connection) -> bool:
        """
        Create the necessary tables if they don't exist.
        Args:
            connection: Active database connection
        Returns:
            bool: True if tables were created successfully
        """
        try:
            cursor = connection.cursor()
            
            # Create customers table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='customers' AND xtype='U')
                CREATE TABLE customers (
                    customer_id INT PRIMARY KEY IDENTITY(1,1),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    phone_number VARCHAR(20),
                    created_at DATETIME DEFAULT GETDATE()
                )
            """)
            
            # Create support_tickets table with additional fields
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='support_tickets' AND xtype='U')
                CREATE TABLE support_tickets (
                    ticket_id INT PRIMARY KEY IDENTITY(1,1),
                    customer_id INT NOT NULL,
                    subject VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    category VARCHAR(100),
                    rating INT,
                    created_at DATETIME DEFAULT GETDATE(),
                    resolved_at DATETIME,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_customer_email')
                CREATE INDEX idx_customer_email ON customers(email)
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ticket_status')
                CREATE INDEX idx_ticket_status ON support_tickets(status)
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ticket_category')
                CREATE INDEX idx_ticket_category ON support_tickets(category)
            """)
            
            connection.commit()
            logger.info("Tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            connection.rollback()
            return False

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

if __name__ == "__main__":
            # Create tables when script is run directly
    conn = create_database_connection()
    if conn:
            create_tables(conn)
            close_connection(conn)
    logger.info("Database connection closed successfully")