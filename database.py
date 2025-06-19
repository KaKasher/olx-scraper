import sqlite3

def initialize_database(db_path):
    """
    Initializes the database and creates the seen_listings table if it doesn't exist.

    Args:
        db_path (str): The path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seen_listings (
            id TEXT PRIMARY KEY,
            found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

def get_seen_listing_ids(db_path):
    """
    Retrieves all listing IDs from the database.

    Args:
        db_path (str): The path to the SQLite database file.

    Returns:
        set: A set of all listing IDs found in the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM seen_listings')
    # Use a set for efficient lookups
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids

def add_listing_ids(db_path, new_ids):
    """
    Adds a list of new listing IDs to the database.

    Args:
        db_path (str): The path to the SQLite database file.
        new_ids (list): A list of new listing ID strings to add.
    """
    if not new_ids:
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Prepare data as a list of tuples for executemany
    data_to_insert = [(listing_id,) for listing_id in new_ids]
    cursor.executemany('INSERT OR IGNORE INTO seen_listings (id) VALUES (?)', data_to_insert)
    conn.commit()
    conn.close() 