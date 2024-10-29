import sqlite3

db = sqlite3.connect("database.db")
# script_file = open("database_create.sql", "r")
# script = script_file.read()
# script_file.close()

# db.executescript(script)
# print("Database created (if not exists)")

# cur = db.cursor()
# cur.execute("INSERT INTO data VALUES (NULL, '2024-23-06 18:18:30', 28, 85)")
# cur.execute("DELETE FROM data WHERE id > 2")
# a = cur.execute("SELECT * FROM data")
# print(a.fetchall())
# db.commit()
# db.close()