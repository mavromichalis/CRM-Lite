from ..db.connection import connect_db

class Product:
    def __init__(self,id,name,price,variants,descr,stock):
        self.id = id
        self.name = name
        self.price = price
        self.variants = variants
        self.descr = descr
        self.stock = stock

    def restock(self,new_stock):
        conn , cur = connect_db()
        temp = self.stock
        try:
            cur.execute(
                """
                UPDATE products SET stock = %s WHERE id = %s
                """
            ,(new_stock,self.id))
            conn.commit()
            self.stock = new_stock
        except Exception:
            self.stock = temp
            conn.rollback()
        finally:
            conn.close()
    