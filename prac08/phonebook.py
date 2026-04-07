import psycopg2
from config import load_config


# 1 Поиск по шаблону

def search_pattern(pattern):
    """Поиск по части имени или телефона"""

    sql = """
    SELECT * FROM users
    WHERE user_name ILIKE %s
       OR phone ILIKE %s;
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:

                like_pattern = "%" + pattern + "%"

                cur.execute(sql,
                            (like_pattern,
                             like_pattern))

                rows = cur.fetchall()

                for row in rows:
                    print("ID:", row[0],
                          "Name:", row[1],
                          "Phone:", row[2])

    except Exception as e:
        print("Ошибка:", e)



# 2Вставка или обновление

def insert_or_update_user(name, phone):
    """Если пользователь есть — обновляет телефон"""

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:

                check_sql = """
                SELECT * FROM users
                WHERE user_name = %s;
                """

                cur.execute(check_sql, (name,))
                user = cur.fetchone()

                if user:
                    update_sql = """
                    UPDATE users
                    SET phone = %s
                    WHERE user_name = %s;
                    """

                    cur.execute(update_sql,
                                (phone, name))

                    print("Телефон обновлён")

                else:
                    insert_sql = """
                    INSERT INTO users (user_name, phone)
                    VALUES (%s, %s);
                    """

                    cur.execute(insert_sql,
                                (name, phone))

                    print("Новый пользователь добавлен")

                conn.commit()

    except Exception as e:
        print("Ошибка:", e)



# 3 Вставка многих пользователей

def insert_many_users(users_list):
    """Вставка списка пользователей"""

    incorrect_data = []

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:

                for name, phone in users_list:

                    # Проверка телефона
                    if not phone.isdigit() or len(phone) < 10:
                        incorrect_data.append(
                            (name, phone)
                        )
                        continue

                    check_sql = """
                    SELECT * FROM users
                    WHERE user_name = %s;
                    """

                    cur.execute(check_sql, (name,))
                    user = cur.fetchone()

                    if user:
                        update_sql = """
                        UPDATE users
                        SET phone = %s
                        WHERE user_name = %s;
                        """

                        cur.execute(update_sql,
                                    (phone, name))

                    else:
                        insert_sql = """
                        INSERT INTO users (user_name, phone)
                        VALUES (%s, %s);
                        """

                        cur.execute(insert_sql,
                                    (name, phone))

                conn.commit()

    except Exception as e:
        print("Ошибка:", e)

    return incorrect_data



# 4 Pagination

def get_users_paginated(limit, offset):
    """Постраничный вывод"""

    sql = """
    SELECT * FROM users
    LIMIT %s OFFSET %s;
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:

                cur.execute(sql,
                            (limit, offset))

                rows = cur.fetchall()

                for row in rows:
                    print("ID:", row[0],
                          "Name:", row[1],
                          "Phone:", row[2])

    except Exception as e:
        print("Ошибка:", e)



# 5 Удаление пользователя
def delete_user(value):
    """Удаление по имени или телефону"""

    sql = """
    DELETE FROM users
    WHERE user_name = %s
       OR phone = %s;
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:

                cur.execute(sql,
                            (value, value))

                conn.commit()

                print("Пользователь удалён")

    except Exception as e:
        print("Ошибка:", e)
