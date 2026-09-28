from ..db.connection import connect_db
from ..models.errors import ProductNotFound,NoStockTracking,AppError,SoldOutProduct

def update_stock(product):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT stock FROM products WHERE id = %s
            """
        ,(product.id,))
        stock = cur.fetchone()[0]
        if not stock:
            raise ProductNotFound 
        if stock[0] == 0:
            raise SoldOutProduct
        if stock[0] == -1:
            raise NoStockTracking
        stock[0] -=1
        cur.execute(
            """
            UPDATE products SET stock = %s WHERE id = %s
            """
        ,(stock[0],product.id))
        conn.commit()
        product.stock = stock
    except ProductNotFound or SoldOutProduct as e:
        return {
            "Code":e.code,
            "Message":e.message,
            "Status Code":e.status_code
        }
    except NoStockTracking:
        return False
    except AppError:
        conn.rollback()
    finally:conn.close()

def add_stock(product_id,added_stock):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT 1 FROM products WHERE id = %s
            """
        ,(product_id,))
        res = cur.fetchone()
        if not res:
            raise ProductNotFound
        cur.execute(
            """
            UPDATE products SET stock = stock + %s WHERE id = %s
            """
        ,(added_stock,product_id))
        conn.commit()
        return True
    except ProductNotFound as e:
        return {
            "Code":e.code,
            "Message":e.message,
            "Status Code":e.status_code
        }
    except AppError:
        conn.rollback()
        return False
    finally: conn.close()
    