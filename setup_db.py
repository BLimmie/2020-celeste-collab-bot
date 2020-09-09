import os
import psycopg2
import json

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

cur.execute("""Drop table Times""")

cur.execute("""
    CREATE TABLE Times (
        id VARCHAR(20) NOT NULL,
        map TEXT NOT NULL,
        time VARCHAR(15) NOT NULL,
        description TEXT NOT NULL
    );
    """)

conn.commit()
