
import sqlite3
import os

# Connect to the database in the current script folder
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "student.db")
connection = sqlite3.connect(db_path)

cursor = connection.cursor()

# Create table first
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT (
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
)
"""

cursor.execute(table_info)

# Insert records only if the table is empty
cursor.execute("SELECT COUNT(*) FROM STUDENT")

if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO STUDENT VALUES (?, ?, ?, ?)",
        [
            ('Siva', 'AI Engineer', 'A', 90),
            ('John', 'Data Science', 'B', 100),
            ('Mukesh', 'Data Science', 'A', 86),
            ('Jacob', 'DEVOPS', 'A', 50),
            ('Dipesh', 'DEVOPS', 'A', 35)
        ]
    )

connection.commit()

# Display records
print("The inserted records are:")

data = cursor.execute("SELECT * FROM STUDENT")

for row in data:
    print(row)

connection.close()

