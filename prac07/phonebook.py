import psycopg2
from config import load_config
def create_tables():
    """ Create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE parts (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
                )
        """,
        """
        CREATE TABLE part_drawings (
                part_id INTEGER PRIMARY KEY,
                file_extension VARCHAR(5) NOT NULL,
                drawing_data BYTEA NOT NULL,
                FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE vendor_parts (
                vendor_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                PRIMARY KEY (vendor_id , part_id),
                FOREIGN KEY (vendor_id)
                    REFERENCES vendors (vendor_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (part_id)
                    REFERENCES parts (part_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the CREATE TABLE statement
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
if __name__ == '__main__':
    create_tables()

def insert_vendor(vendor_name):
    """ Insert a new vendor into the vendors table """
    sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
    vendor_id = None
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                cur.execute(sql, (vendor_name,))
                rows = cur.fetchone()
                if rows:
                    vendor_id = rows[0]
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    return vendor_id
if __name__ == '__main__':
    insert_vendor("3M Co.")


def insert_many_vendors(vendor_list):
    """ Insert multiple vendors into the vendors table  """
    sql = "INSERT INTO vendors(vendor_name) VALUES(%s) RETURNING *"
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                cur.executemany(sql, vendor_list)
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if __name__ == '__main__':
         insert_many_vendors([
        ('AKM Semiconductor Inc.',),
        ('Asahi Glass Co Ltd.',),
        ('Daikin Industries Ltd.',),
        ('Dynacast International Inc.',),
        ('Foster Electric Co. Ltd.',),
        ('Murata Manufacturing Co. Ltd.',)
    ])
         
         import psycopg2
from config import load_config

def insert_user(name, phone):
    sql = """
    INSERT INTO users (user_name, phone)
    VALUES (%s, %s);
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, phone))
                conn.commit()
                print("Данные успешно добавлены")
    except Exception as e:
        print("Ошибка:", e)


if __name__ == "__main__":
    name = input("Введите имя: ")
    phone = input("Введите телефон: ")

    insert_user(name, phone)



    import psycopg2
from config import load_config

def update_contact(user_id, new_name=None, new_phone=None):

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:

                
                if new_name:
                    sql_name = """
                    UPDATE users
                    SET user_name = %s
                    WHERE user_id = %s;
                    """
                    cur.execute(sql_name, (new_name, user_id))

                
                if new_phone:
                    sql_phone = """
                    UPDATE users
                    SET phone = %s
                    WHERE user_id = %s;
                    """
                    cur.execute(sql_phone, (new_phone, user_id))

                conn.commit()
                print("Контаr обновлён")

    except Exception as e:
        print("Ошибка:", e)

        import psycopg2
from config import load_config

def find_by_name(name):

    sql = """
    SELECT * FROM users
    WHERE user_name ILIKE %s;
    """

    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, ('%' + name + '%',))
                rows = cur.fetchall()

                for row in rows:
                    print("ID:", row[0],
                          "Name:", row[1],
                          "Phone:", row[2])

    except Exception as e:
        print("Ошибка:", e)


    def find_by_phone_prefix(prefix):

            sql = """
                SELECT * FROM users
                WHERE phone LIKE %s;
            """

            config = load_config()

            try:
                     with psycopg2.connect(**config) as conn:
                         with conn.cursor() as cur:
                             cur.execute(sql, (prefix + '%',))
                             rows = cur.fetchall()

                     for row in rows:
                            print("ID:", row[0],
                                 "Name:", row[1],
                                 "Phone:", row[2])

            except Exception as e:
             print("Ошибка:", e)