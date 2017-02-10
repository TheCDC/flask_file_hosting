import sqlite3


def main():
    connection = sqlite3.connect("database.db")
    c = connection.cursor()

    try:
        c.execute(
            "CREATE TABLE files (id INTEGER PRIMARY KEY AUTOINCREMENT, date text, path text)")
    except sqlite3.OperationalError:
        print("INFO: files db table already exists or there was an error initializing.")

    connection.commit()
    connection.close()
if __name__ == '__main__':
    main()
