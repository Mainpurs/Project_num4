import sqlite3
from typing import List, Any


def execute_query(db_file, query, data=None):
    try:
        con = sqlite3.connect(db_file)
        cursor = con.cursor()

        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        con.commit()
        con.close()

        return cursor

    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса:", e)


def execute_selection_query(db_path, query, data=None):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        connection.close()
        return rows

    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса:", e)


# ----------------------------------------------Add---------------------------------------------------------------------
def add_user(db_file, tg_id, status, admin, user_prompt, subject, lvl, ANSWER):
    if tg_id == 5932532601:
        admin = 1

    query = '''INSERT INTO data (tg_id, status, admin, user_prompt, subject, lvl, ANSWER) 
            VALUES (?, ?, ?, ?, ?, ?, ?);'''

    data = (tg_id, status, admin, user_prompt, subject, lvl, ANSWER)

    execute_query(db_file, query, data)


# ----------------------------------------------Answer------------------------------------------------------------------
def update_row_value(db_file, tg_id, column_name, new_value):
    if user_in(db_file, 'tg_id', tg_id):
        query = f'UPDATE data SET {column_name} = ? WHERE tg_id = {tg_id}'

        data = (new_value,)

        execute_query(db_file, query, data)
    else:
        print("Такого пользователя нет :(")


# -----------------------------------------------Delete-----------------------------------------------------------------
def delete_user(db_file, tg_id):

    query = 'delete from data where tg_id=?;'

    data = (tg_id,)

    execute_query(db_file, query, data)


# --------------------------------------Проверка_на_наличие_пользователя------------------------------------------------
def user_in(db_file, column_name, value):
    query = f'SELECT {column_name} FROM data WHERE {column_name} = ?'
    data = (value,)
    row = execute_selection_query(db_file, query, data)
    print(row)
    return row


# -------------------------------------------Инфа_по_пользователю-------------------------------------------------------
def get_data_for_user(db_file, tg_id):
    if user_in(db_file, 'tg_id', tg_id):
        query = f'SELECT tg_id, subject, lvl, user_prompt, ANSWER, status ' \
                    f'FROM data where tg_id = ? limit 1'

        row = execute_selection_query(db_file, query, data=[tg_id])[0]
        result = {
            'subject': row[1],
            'lvl': row[2],
            'user_prompt': row[3],
            'ANSWER': row[4],
            'status': row[5]
        }
        print(result)
        return result
    else:
        print("Такого пользователя нет :(")
        return []
