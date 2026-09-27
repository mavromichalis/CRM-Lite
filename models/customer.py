from ..db.connection import connect_db
from ..utils.logs import generate_logs
from ..utils.id_generator import generate_id
from ..services.customers import *

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
        if append_order(self.id,order_no):
            self.orders.append(order_no)

    def get_customer_orders(self):
        return fetch_orders(self.id)
    

    def change_status(self,new_status):
        if update_status(self.id,new_status) == True:
            self.status = new_status

    def get_info(self):
        return {
            "Customer ID":self.id,
            "Customer Type":self.type,
            "First Name":self.f_name,
            "Last Name":self.l_name,
            "VAT":self.vat,
            "Phone":self.phone,
            "Address":self.address,
            "Orders":self.orders,
            "Created at":self.created_at,
            "Last modified":self.last_modified,
            "Status":self.status
        }