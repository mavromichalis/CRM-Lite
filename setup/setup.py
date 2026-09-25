from ..services.users import create_user
from ..utils.hasher import hash
from ..utils.logs import generate_logs
import sys

def main():
    print("~~CRM_Lite initial setup~~")
    while True:
        q1 = input("Is your .env ready in the root folder? (Y/N) \n >>>")
        if q1 == 'N':
            sys.exit()
        elif q1 == 'Y':
            break
        else:
            print("Try again! wrong input!!")

    
