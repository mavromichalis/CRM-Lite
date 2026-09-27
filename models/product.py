from ..db.connection import connect_db
from ..services.products import * 

class Product:
    def __init__(self,id,name,price,variants,descr,stock):
        self.id = id
        self.name = name
        self.price = price
        self.variants = variants
        self.descr = descr
        self.stock = stock

    def restock(self,added_stock):
        if add_stock(self.id,added_stock) == True:
            self.stock+=added_stock
            

    