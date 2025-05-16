import sqlite3

def setup_database():
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            name TEXT PRIMARY KEY,
            age INTEGER,
            location TEXT,
            gender TEXT
        )
    ''')

    # Insert sample data (only if table is empty)
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('Nagendhar', 30, 'Hyderabad', 'Male'),
            ('Priya', 25, 'Bangalore', 'Female'),
            ('Arun', 35, 'Chennai', 'Male'),
            ('Sneha', 28, 'Mumbai', 'Female')
        ]
        cursor.executemany('INSERT INTO customers (name, age, location, gender) VALUES (?, ?, ?, ?)', sample_data)

    conn.commit()
    conn.close()

def add_customer(name: str, age: int, location: str, gender: str):
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO customers (name, age, location, gender) VALUES (?, ?, ?, ?)',
                      (name, age, location, gender))
        conn.commit()
        return {"message": f"Customer {name} added successfully"}
    except sqlite3.IntegrityError:
        return {"error": f"Customer with name {name} already exists"}
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}
    finally:
        conn.close()

def fetch_customer(name: str = None):
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    try:
        if name:
            cursor.execute('SELECT * FROM customers WHERE name = ?', (name,))
            result = cursor.fetchone()
            if not result:
                return {"error": f"No customer found with name {name}"}
            columns = ['name', 'age', 'location', 'gender']
            return dict(zip(columns, result))
        else:
            cursor.execute('SELECT * FROM customers')
            results = cursor.fetchall()
            if not results:
                return {"message": "No customers found"}
            columns = ['name', 'age', 'location', 'gender']
            return [dict(zip(columns, row)) for row in results]
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}
    finally:
        conn.close()

def execute_query(query: str):
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        if not results:
            return {"message": "No results found"}
        return [dict(zip(columns, row)) for row in results]
    except sqlite3.Error as e:
        return {"error": f"Error executing query: {e}"}
    finally:
        conn.close()