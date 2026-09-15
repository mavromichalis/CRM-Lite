from ..db.connection import connect_db
from ..utils.logs import generate_logs
from ..utils.id_generator import generate_id

class Customer:
    def __init__(self,id,type,f_name,l_name,vat,phone,address,orders,created_at,last_modified,status):
        self.id = id
        self.type = type
        self.f_name = f_name
        self.l_name = l_name
        self.vat = vat 
        self.phone = phone
        self.address = address
        self.orders = orders
        self.created_at = created_at
        self.last_modified =  last_modified
        self.status = status

    def add_order(self,order_no):
        conn , cur = connect_db()
        self.orders.append(order_no)
        try:
            cur.execute(
                """
                UPDATE customers SET orders = %s WHERE id = %s 
                """
            ,(self.orders,self.id))
            conn.commit()
        except:
            conn.rollback()
            self.orders.remove(order_no)
        finally:
            conn.close()

    def get_customer_orders(self):
        conn , cur = connect_db()
        try:
            cur.execute(
                """
                SELECT * FROM orders WHERE customer_id = %s
                """
            ,(self.id,))
            return cur.fetchall()
        finally:
            conn.close()
    


    def change_status(self,new_status):
        conn , cur = connect_db()
        try:
            cur.execute(
                """
                UPDATE customers SET status = %s WHERE id = %s
                """
            ,(new_status,self.id))
            conn.commit()
            self.status = new_status
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    