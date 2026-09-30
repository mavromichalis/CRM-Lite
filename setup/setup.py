"""Create the first CRM-Lite administrator account."""

import secrets
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    from db.connection import connect_db
    from utils.hasher import hash as hash_password
except ImportError as exc:
    raise SystemExit(
        "Install the project dependencies first: python -m pip install -r requirements.txt"
    ) from exc


def create_first_admin(username, password, real_name):
    conn, cur = connect_db()
    try:
        cur.execute("SELECT EXISTS (SELECT 1 FROM users)")
        if cur.fetchone()[0]:
            raise ValueError("An account already exists. Run app.py and sign in instead.")

        for _ in range(100):
            user_id = secrets.randbelow(90_000_000) + 10_000_000
            cur.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
            if cur.fetchone() is None:
                break
        else:
            raise RuntimeError("Could not generate an account ID. Please try again.")

        cur.execute(
            "INSERT INTO users (id, username, password_hash, real_name, role, is_active) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, username, hash_password(password), real_name, "admin", "active"),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def submit():
    username = username_entry.get().strip()
    password = password_entry.get()
    real_name = real_name_entry.get().strip()
    if not username or not password or not real_name:
        messagebox.showwarning("Missing information", "Enter a username, password, and name.", parent=root)
        return
    try:
        create_first_admin(username, password, real_name)
    except ValueError as exc:
        messagebox.showerror("Setup already completed", str(exc), parent=root)
        root.destroy()
    except Exception as exc:
        messagebox.showerror("Could not create account", str(exc), parent=root)
        return
    messagebox.showinfo("Setup complete", "Administrator account created. You can now open app.py and sign in.", parent=root)
    root.destroy()


root = tk.Tk()
root.title("CRM-Lite setup")
root.resizable(False, False)
root.configure(padx=24, pady=20)

tk.Label(root, text="Set up CRM-Lite", font=("TkDefaultFont", 16, "bold")).grid(
    row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
)
tk.Label(root, text="Create the first administrator account.").grid(
    row=1, column=0, columnspan=2, sticky="w", pady=(0, 18)
)

tk.Label(root, text="Username").grid(row=2, column=0, sticky="w", pady=5)
username_entry = tk.Entry(root, width=32)
username_entry.grid(row=2, column=1, sticky="ew", padx=(16, 0), pady=5)

tk.Label(root, text="Password").grid(row=3, column=0, sticky="w", pady=5)
password_entry = tk.Entry(root, width=32, show="*")
password_entry.grid(row=3, column=1, sticky="ew", padx=(16, 0), pady=5)

tk.Label(root, text="Name").grid(row=4, column=0, sticky="w", pady=5)
real_name_entry = tk.Entry(root, width=32)
real_name_entry.grid(row=4, column=1, sticky="ew", padx=(16, 0), pady=5)

tk.Button(root, text="Create administrator", command=submit).grid(
    row=5, column=0, columnspan=2, sticky="ew", pady=(18, 0)
)
username_entry.focus_set()
root.bind("<Return>", lambda _event: submit())
root.mainloop()
