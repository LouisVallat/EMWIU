import sqlite3
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect("API.db")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS emwiu(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, url TEXT, email TEXT, ip TEXT, starttime TEXT)"
)
conn.commit()
cursor.execute("""SELECT * FROM emwiu""")
rows = cursor.fetchall()
conn.close()

for row in rows:
    print(row)
