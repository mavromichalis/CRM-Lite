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
    
        