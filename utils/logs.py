from ..db.connection import connect_db
import datetime as dt
from .id_generator import generate_log_id

def generate_logs(user,event):
    time = str(dt.now())
    conn,cur = connect_db()
    log_id = generate_log_id()
    try:
        cur.execute(
            """
            INSERT into logs (id,user_id,timestamp,action) VALUES (%s,%s,%s,%s)
            """
        ,(log_id,user,time,event))
        conn.commit()
        return id 
    except Exception:
        return None
    finally:
        conn.close()
        