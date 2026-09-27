from ..db.connection import connect_db
from datetime import datetime
from ..utils.id_generator import generate_id

def add_customer(type,f_name,l_name,vat,phone,address,status):
    conn,cur = connect_db()
    id = generate_id('customers')
    try:
        cur.execute(
            """
            INSERT INTO customers (id,type,f_name,l_name,vat,phone,address,orders,created_at,last_modified,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
        ,(id,type,f_name,l_name,vat,phone,address,[],datetime.now(),datetime.now(),status))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()