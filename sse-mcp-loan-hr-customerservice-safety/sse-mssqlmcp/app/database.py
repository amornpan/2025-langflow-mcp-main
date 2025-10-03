"""
Database connection and utilities
"""
import os
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DB_SERVER = os.getenv('DB_SERVER', '34.47.90.27')
DB_NAME = os.getenv('DB_NAME', 'Electric')
DB_USER = os.getenv('DB_USER', 'SA')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Passw0rd123456')

# Create SQLAlchemy engine
engine: Optional[Engine] = None

def get_engine() -> Engine:
    """Get or create database engine"""
    global engine
    if engine is None:
        connection_string = f'mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
        engine = create_engine(connection_string)
        logger.info("Database engine created")
    return engine

def get_connection() -> Optional[Connection]:
    """Get a database connection"""
    try:
        return get_engine().connect()
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def get_tables() -> List[str]:
    """Get all table names in the database"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        query = text("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        result = conn.execute(query)
        tables = [row[0] for row in result]
        return tables
    except Exception as e:
        logger.error(f"Error fetching tables: {e}")
        return []
    finally:
        conn.close()

def get_table_schema(table_name: str) -> Optional[List[Dict[str, Any]]]:
    """Get the schema for a specific table"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        query = text(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
        """)
        
        result = conn.execute(query, {"table_name": table_name})
        columns = []
        
        for row in result:
            col_name, data_type, max_length, is_nullable, default = row
            column_info = {
                "name": col_name,
                "type": data_type,
                "max_length": max_length,
                "nullable": is_nullable == 'YES',
                "default": default
            }
            columns.append(column_info)
            
        return columns
    except Exception as e:
        logger.error(f"Error fetching schema for table {table_name}: {e}")
        return None
    finally:
        conn.close()

def execute_query(query: str) -> Dict[str, Any]:
    """Execute a SQL query and return results"""
    conn = get_connection()
    if not conn:
        return {"error": "Could not connect to the database."}
    
    try:
        # Execute query using pandas for better formatting
        df = pd.read_sql(text(query), conn)
        
        if df.empty:
            return {"result": "Query executed successfully but returned no results."}
        
        # Format result
        result = df.to_string(index=False)
        
        # Limit result size
        if len(result) > 10000:
            result = df.head(100).to_string(index=False)
            result += f"\n\n[Showing only 100 of {len(df)} rows]"
        
        return {"result": result}
    except Exception as e:
        return {"error": f"Error executing query: {str(e)}"}
    finally:
        conn.close()

def get_database_info() -> Dict[str, Any]:
    """Get general information about the database"""
    conn = get_connection()
    if not conn:
        return {"error": "Could not connect to the database."}
    
    info = {
        "database_name": DB_NAME,
        "server": DB_SERVER,
    }
    
    try:
        # Get table count
        tables = get_tables()
        info["table_count"] = len(tables)
        
        # Get database version
        query_version = text("SELECT @@VERSION")
        result = conn.execute(query_version)
        version = result.fetchone()[0]
        info["server_version"] = version
        
        # Get database size
        query_size = text("SELECT SUM(size/128.0) FROM sys.database_files;")
        result = conn.execute(query_size)
        size_mb = result.fetchone()[0]
        info["size_mb"] = round(float(size_mb), 2) if size_mb else None
        
    except Exception as e:
        info["error"] = str(e)
    finally:
        conn.close()
    
    return info

# Cache for tables and schemas
class DatabaseCache:
    """Simple cache for database metadata"""
    def __init__(self):
        self.tables: Optional[List[str]] = None
        self.schemas: Dict[str, List[Dict[str, Any]]] = {}
    
    def refresh(self):
        """Refresh the cache"""
        logger.info("Refreshing database cache...")
        self.tables = get_tables()
        self.schemas = {}
        for table in self.tables:
            schema = get_table_schema(table)
            if schema:
                self.schemas[table] = schema
        logger.info(f"Cache refreshed. Found {len(self.tables)} tables.")
    
    def get_tables(self) -> List[str]:
        """Get cached tables"""
        if self.tables is None:
            self.refresh()
        return self.tables or []
    
    def get_schema(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached schema for a table"""
        if table_name not in self.schemas:
            schema = get_table_schema(table_name)
            if schema:
                self.schemas[table_name] = schema
        return self.schemas.get(table_name)

# Initialize cache
db_cache = DatabaseCache()
