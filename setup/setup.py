from ..services.users import create_user
from tkinter import * 
import tkinter as tk
import os
from dotenv import set_key
from dotenv import load_dotenv
from pathlib import Path
import sys

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv()
if os.environ["SETUP_STATUS"] == 1:
    sys.exit()



root = tk.Tk()
username_entry = Entry(root)
password_entry = Entry(root,show="*")
real_name_entry = Entry(root)
def submit():
    username = username_entry.get()
    password = password_entry.get()
    real_name = real_name_entry.get()
    user = create_user(username,password,real_name,'admin','active')
    if user is object:
        set_key(env_path,'SETUP_STATUS','1')
        new = Toplevel(root)
        Label(new,text="User created. You can delete the setup folder.")
        new.mainloop()
    else:
        new = Toplevel(root)
        Label(new,text="Error. Try again")
        new.mainloop()

Label(root,text="Welcome to the innitial setup of CRMLite").pack()
Label(root,text="Create the first user (will be an active admin.)").pack()
Label(root,text='Account username')
username_entry.pack()
Label(root,text='Password').pack()
password_entry.pack()
Label(root,text="Real name").pack()
real_name_entry.pack()
Button(root,text="Sign up",command=submit).pack()

env_path = Path(".env")

root.mainloop()