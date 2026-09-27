from ..db.connection import connect_db
from ..models.order import Order
from ..utils.id_generator import generate_id

def create_order(status,customer_id,products):
    conn , cur = connect_db()
    id = generate_id('orders')
    try:
        price = 0 
        for product in products:
            cur.execute(
                """
                SELECT price FROM products WHERE id = %s
                """
            ,(product))
            res = cur.fetchone()
            if res is None:
                raise Exception
            price+=res[0]
        cur.execute(
            """
            INSERT INTO orders (id,status,customer_id,products,price) VALUES (%s,%s,%s,%s,%s)
            """
        ,(id,status,customer_id,products,price))
        conn.commit()
        return Order(id,status,customer_id,products,price)
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()

def update_order_status(id,new_status):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            UPDATE orders SET status = %s WHERE id = %s
            """
        ,(new_status,id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()