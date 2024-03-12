import sqlite3


def prepare_database():
    try:
        # Установка соединения с базой данных
        con = sqlite3.connect('sqliteData.db')
        cur = con.cursor()

        # Создание таблицы students, если она не существует
        cur.execute('''CREATE TABLE IF NOT EXISTS data (
                            id INTEGER PRIMARY KEY,
                            tg_id INTEGER,
                            status INTEGER,
                            admin INTEGER,
                            user_prompt TEXT,
                            subject TEXT,
                            lvl INTEGER,
                            ANSWER TEXT
                       )''')

        # Фиксация изменений и закрытие соединения
        con.commit()
    except sqlite3.Error as e:
        print("Ошибка при работе с SQLite:", e)
    finally:
        con.close()


prepare_database()
