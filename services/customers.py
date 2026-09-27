from ..db.connection import connect_db
from datetime import datetime
from ..utils.id_generator import generate_id
from ..models.customer import Customer
from ..models.errors import CustomerNotFound

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

def append_order(id,order_id):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT orders FROM customers WHERE id = %s
            """
        ,(id,))
        res = cur.fetchone()
        if not res:
            raise CustomerNotFound
        current_orders = res[0]
        current_orders.append(order_id)
        cur.execute(
            """
            UPDATE customers SET orders = %s WHERE id = %s
            """
        ,(current_orders,id))
        conn.commit()
        return True
    except CustomerNotFound:
        return {
            "Code":CustomerNotFound.code,
            "Message":CustomerNotFound.message,
            "Status Code":CustomerNotFound.status_code
        }
    except Exception:
        conn.rollback()
        return False
    finally: conn.close()

def fetch_orders(id):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT * FROM orders WHERE customer_id = %s
            """
        ,(id,))
        return cur.fetchall()
    finally:
        conn.close()

def update_status(id,new_status):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT 1 FROM customers WHERE id = %s
            """
        )
        res = cur.fetchone()
        if not res:
            raise CustomerNotFound
        cur.execute(
            """
            UPDATE customers SET status = %s WHERE id = %s
            """
        ,(new_status,id))
        conn.commit()
        return True
    except CustomerNotFound:
        return {
            "Code":CustomerNotFound.code,
            "Message":CustomerNotFound.message,
            "Status Code":CustomerNotFound.status_code
        }
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def generate_object(id):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT * FROM users WHERE id = %s
            """
        ,(id))
        res = cur.fetchone()
        if not res: raise Exception
        return Customer(id,res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10])
    except Exception:
        conn.rollback()
        return None
    finally: conn.close()