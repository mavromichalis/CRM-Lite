from ..db.connection import connect_db

def update_stock(product):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT stock FROM products WHERE id = %s
            """
        ,(product.id,))
        stock = cur.fetchone()[0]
        if stock is None:
            raise Exception 
        if stock == -1 or stock == 0:
            raise Exception
        stock -=1
        cur.execute(
            """
            UPDATE products SET stock = %s WHERE id = %s
            """
        ,(stock,product.id))
        conn.commit()
        product.stock = stock
    except Exception:
        conn.rollback()
    finally:conn.close()

def add_stock(product_id,added_stock):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            UPDATE products SET stock = stock + %s WHERE id = %s
            """
        ,(added_stock,product_id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally: conn.close()
    