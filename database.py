import mysql.connector
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

connection_pool = None


def get_pool():
    """Initializes and returns the connection pool."""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
            logger.info("Database connection pool created successfully.")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise  # Re-raise the exception if pool creation fails
    return connection_pool


def get_connection():
    """Gets a connection from the pool."""
    pool = get_pool()
    return pool.get_connection()


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Executes a SQL query using a connection from the pool."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        # Use dictionary cursor if fetching data, else standard
        cursor = conn.cursor(dictionary=(fetch_one or fetch_all))
        cursor.execute(query, params)

        if commit:
            conn.commit()
            return cursor.lastrowid

        if fetch_one:
            return cursor.fetchone()

        if fetch_all:
            return cursor.fetchall()

        return None

    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}. Query: {query}, Params: {params}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()  # Returns connection to the pool


def insert_customer(unique_id, name, email, face_encoding, last_visited, visit_count):
    query = """
        INSERT INTO customers
        (unique_id, name, email, face_encoding, last_visited, visit_count)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(
        query,
        (unique_id, name, email, face_encoding, last_visited, visit_count),
        commit=True,
    )


def update_customer_visit(unique_id):
    query = """
        UPDATE customers
        SET last_visited = NOW(), visit_count = visit_count + 1
        WHERE unique_id = %s
    """
    return execute_query(query, (str(unique_id),), commit=True)


def fetch_all_customers_for_rec():
    # Fetching with dictionary=True
    query = "SELECT unique_id, name, email, face_encoding FROM customers WHERE face_encoding IS NOT NULL"
    return execute_query(query, fetch_all=True)


def fetch_schema():
    """Fetch the schema of all tables in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    schema_str = ""
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for (table,) in tables:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            cols = cursor.fetchall()
            schema_str += f"\nTable `{table}`:\n"
            for col in cols:
                schema_str += f"  - {col[0]} ({col[1].decode('utf-8') if isinstance(col[1], bytes) else col[1]})\n"
    except Exception as e:
        logger.error(f"Error fetching schema: {e}")
    finally:
        cursor.close()
        conn.close()
    return schema_str


def run_query(sql_query):
    """Runs a given SQL query (potentially from LLM) and fetches all results."""
    # Note: Using fetch_all=True implies a dictionary cursor.
    # LLM queries might return different structures, so raw tuples might be safer
    # or adjust this based on expected LLM output.
    conn = get_connection()
    cursor = conn.cursor()  # Using standard tuple cursor here.
    results = None
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Error running LLM query: {e}. Query: {sql_query}")
        raise  # Re-raise to be handled in utils.py
    finally:
        cursor.close()
        conn.close()
    return results
