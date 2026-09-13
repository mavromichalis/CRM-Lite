import random as r 
from ..db.connection import connect_db
from psycopg2 import sql

def generate_id(table):
    conn, cur = connect_db()
    try:
        while True:
            possible_id = r.randint(100000, 999999)
            cur.execute(
                sql.SQL("SELECT 1 FROM {} WHERE id = %s").format(sql.Identifier(table)),
                (possible_id,)
            )
            if cur.fetchone() is None:
                return possible_id
    finally:
        conn.close()
                    
def generate_log_id():
    conn, cur = connect_db()
    try:
        while True:
            possible_id = r.randint(10000000, 99999999)
            cur.execute(
                """
                SELECT 1 FROM logs WHERE id = %s
                """
            ,(possible_id,))
            if cur.fetchone() is None:
                return possible_id
    finally:
        conn.close()