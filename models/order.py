from ..db.connection import connect_db

class Order:
    def __init__(self,id,status,customer_id,products,price):
        self.id = id
        self.status = status
        self.customer_id = customer_id 
        self.products = products 
        self.price = price

    def update_status(self,new_status):
        conn , cur = connect_db()
        try:
            cur.execute(
                """
                UPDATE orders SET status = %s WHERE id = %s
                """
            ,(new_status,self.id))
            conn.commit()
            self.status = new_status
        except Exception:
            conn.rollback()
        finally:
            conn.close()
    
    