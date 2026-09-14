from ..db.connection import connect_db

class Order:
    def __init__(self,id,status,customer_id,products,price):
        self.id = id
        self.status = status
        self.customer_id = customer_id 
        self.products = products 
        self.price = price

    