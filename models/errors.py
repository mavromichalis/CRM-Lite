import psycopg2

class AppError(Exception):
    code = "UNKNOWN_ERROR"
    message = "An unknown error occured."
    status_code = 101 

class PostgresError(psycopg2.Error):
    code="DATABASE_ERROR"
    message = "Error in your database"
    status_code = 102

class InactiveAccount(AppError):
    code = "INACTIVE_ACCOUNT"
    message = "Account is not active."
    status_code = 301

class WrongPassword(AppError):
    code = "WRONG_PASSWORD"
    message = "Wrong Password"
    status_code = 302

class UserDoesNotExist(AppError):
    code = "USER_NOT_FOUND"
    message = "User not found"
    status_code = 303 

class UsernameTaken(AppError):
    code = "USERNAME_TAKEN"
    message = "Username Taken"
    status_code = 304

class CustomerNotFound(AppError):
    code="CUSTOMER_NOT_FOUND"
    message = "Customer not found."
    status_code = 501


class OrderNotFound(AppError):
    code="ORDER_NOT_FOUND"
    message = "Order not found."
    status_code = 601

class ProductNotFound(AppError):
    code="PRODUCT_NOT_FOUND"
    message = "Product not found"
    status_code = 401

class NoStockTracking(Exception):
    code="NO_STOCK_TRACKING"
    message = "Product does not track stock"
    status_code = 402

class SoldOutProduct(Exception):
    code="SOLD_OUT_PORDUCT"
    message = "Product sold out"
    status_code = 403

