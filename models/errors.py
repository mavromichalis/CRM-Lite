class AppError(Exception):
    code = "UNKNOWN_ERROR"
    message = "An unknown error occured."
    status_code = 101 

class InactiveAccount(Exception):
    code = "INACTIVE_ACCOUNT"
    message = "Account is not active."
    status_code = 301

class WrongPassword(Exception):
    code = "WRONG_PASSWORD"
    message = "Wrong Password"
    status_code = 302

class UserDoesNotExist(Exception):
    code = "USER_NOT_FOUND"
    message = "User not found"
    status_code = 303 

class UsernameTaken(Exception):
    code = "USERNAME_TAKEN"
    message = "Username Taken"
    status_code = 304

class CustomerNotFound(Exception):
    code="CUSTOMER_NOT_FOUND"
    message = "Customer not found."
    status_code = 501


class OrderNotFound(Exception):
    code="ORDER_NOT_FOUND"
    message = "Order not found."
    status_code = 601

