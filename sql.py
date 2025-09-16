import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",       # or your MySQL server IP
    user="root",            # change to your MySQL username
    password="KAERMORHEN2311" # change to your MySQL password
)

cursor = conn.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS cloud_kitchen")
cursor.execute("USE cloud_kitchen")

# Create Orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    items TEXT,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create Inventory table
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    item VARCHAR(100) PRIMARY KEY,
    quantity DECIMAL(10,2),
    threshold DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
""")

# Create Expenses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    amount DECIMAL(10,2),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert sample data
cursor.execute("INSERT INTO orders (platform, items, total_amount, status) VALUES (%s, %s, %s, %s)",
               ("Zomato", "Burger, Fries", 250.00, "Completed"))

cursor.execute("INSERT INTO inventory (item, quantity, threshold) VALUES (%s, %s, %s)",
               ("Chicken", 10.00, 2.00))

cursor.execute("INSERT INTO expenses (type, amount) VALUES (%s, %s)",
               ("Raw Material", 1200.00))

conn.commit()
print("✅ Database and tables created with sample data.")

# Fetch & print
cursor.execute("SELECT * FROM orders")
print("\n📦 Orders:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM inventory")
print("\n📦 Inventory:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM expenses")
print("\n📦 Expenses:")
for row in cursor.fetchall():
    print(row)

conn.close()
