import sqlite3


def start(chat_id):

    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    cursor.execute(f"""
    CREATE TABLE admins
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE)""")

    cursor.execute(f"INSERT INTO admins (chat_id) VALUES ({chat_id})")

    connect.commit()
    connect.close()


def is_admin(chat_id):
    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    sql_req = cursor.execute(f"SELECT chat_id FROM admins")

    for admin in sql_req.fetchall():
        if str(chat_id) == str(admin[0]):
            return 1
        else:
            continue

    connect.close()


def add_admin(chat_id):
    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    cursor.execute(f"INSERT INTO admins (chat_id) VALUES ({chat_id})")

    connect.commit()
    connect.close()


def create_table(bot_name):
    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    cursor.execute(f"""
    CREATE TABLE {bot_name}
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT,
    description TEXT
    )""")

    connect.close()


def delete_bot(bot_name):
    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    cursor.execute(f"DROP TABLE {bot_name}")

    connect.commit()
    connect.close()


def count():
    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    sql_req = cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table';""")

    tables_count = 0
    for table in sql_req.fetchall():
        if table[0] != "admins" and table[0] != "sqlite_sequence":
            tables_count += 1

    connect.close()

    return tables_count


def bots_elems():
    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    sql_req = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")

    bots_list = []
    for table in sql_req.fetchall():
        if table[0] != "admins" and table[0] != "sqlite_sequence":
            bots_list.append(table[0])

    return bots_list


def add_command(bot_name, commands_list):

    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    cursor.execute(f"DROP TABLE {bot_name};")
    cursor.execute(f"""CREATE TABLE {bot_name}
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT,
    description TEXT
    );""")

    for command in commands_list:
        cursor.execute(f"""
        INSERT INTO {bot_name} (command, description) 
        VALUES ('{command.split(" - ")[0]}', '{command.split(" - ")[1]}')""")

    connect.commit()
    connect.close()


def dict_commands(bot_name):
    dict1 = {}

    connect = sqlite3.connect("bots.db")
    cursor = connect.cursor()

    sql_req = cursor.execute(f"SELECT command, description FROM {bot_name}")

    for command in sql_req.fetchall():
        dict1[command[0]] = command[1]

    connect.close()

    return dict1
