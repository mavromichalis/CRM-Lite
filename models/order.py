from ..services.orders import *

class Order:
    def __init__(self,id,status,customer_id,products,price):
        self.id = id
        self.status = status
        self.customer_id = customer_id 
        self.products = products 
        self.price = price

    def update_status(self,new_status):
        if update_order_status(self.id,new_status) == True:
            self.status = new_status

    
    
    