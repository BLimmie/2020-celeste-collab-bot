from datetime import time

SUCCESS = 1
FAIL = None


def fetch_member(conn, id):
    """
        Return a member from the database as a tuple.
        args:
        conn = database connection. Typically bot.conn
        id = member.id
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Times where id = '%s';", (id,))
        return cur.fetchall()
    except Exception as e:
        print(e)
        conn.rollback()
        return FAIL


def fetch_times(conn, name):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Times where map LIKE %s;", (name,))
        return cur.fetchall()
    except Exception as e:
        print(e)
        conn.rollback()
        return FAIL


def insert_time(conn, member_id, map_name: str, map_time: str):
    """
        Insert an IL time into the database
        args:
        conn = database connection. Typically bot.conn
        member_id = member.id
        map_name = name of map ran
    """
    # Check if time exists
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Times WHERE id = '%s' AND map = %s;", (member_id, map_name))
        result = cur.fetchone()
        time_exists = result is not None
    except Exception as e:
        print(e)
        conn.rollback()
        return FAIL
    if time_exists:
        previous_time = time.fromisoformat(result[2])
        new_time = time.fromisoformat(map_time)
        print(previous_time, new_time)
        if new_time >= previous_time:
            return 2  # Time is worse than previous time
        try:
            cur = conn.cursor()
            cur.execute("UPDATE Times SET time = %s WHERE id = '%s' AND map = %s;", (map_time, member_id, map_name))
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return FAIL
    else:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO Times (id, map, time) VALUES (%s, %s, %s);", (member_id, map_name, map_time))
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return FAIL
    return SUCCESS

def get_counter(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Bugcounter")
        return cur.fetchone()[0]
    except Exception as e:
        print(e)
        conn.rollback()
        return FAIL

def increment_counter(conn):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE Bugcounter SET count=count+1")
        conn.commit()
        return SUCCESS
    except Exception as e:
        print(e)
        conn.rollback()
        return FAIL

def get_and_increment_counter(conn):
    res = get_counter(conn)
    increment_counter(conn)
    return res