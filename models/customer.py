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

    #TODO def add_order(self,order_no):

    def change_status(self,new_status):
        conn , cur = connect_db()
        try:
            cur.execute(
                """
                UPDATE clients SET status = %s WHERE id = %s
                """
            ,(new_status,self.id))
            conn.commit()
            self.status = new_status
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    