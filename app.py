"""A lightweight Tkinter desktop interface for CRM-Lite."""

from __future__ import annotations

import secrets
import tkinter as tk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().with_name(".env"))
    from db.connection import connect_db
    from utils.hasher import hash as hash_password
except ImportError as exc:
    raise SystemExit(
        "CRM-Lite needs psycopg2 and python-dotenv installed before it can start."
    ) from exc


BG = "#f5f7fb"
WHITE = "#ffffff"
INK = "#172033"
MUTED = "#718096"
ACCENT = "#3157d5"
ACCENT_DARK = "#2546b8"
LINE = "#e5eaf2"
SIDEBAR = "#18233b"
SIDEBAR_MUTED = "#a9b4c9"
GREEN = "#16835d"
RED = "#c13c4a"


def db_query(query, params=(), fetch="all", commit=False):
    """Run a small database operation and always close its connection."""
    conn, cur = connect_db()
    try:
        cur.execute(query, params)
        result = cur.fetchone() if fetch == "one" else cur.fetchall() if fetch == "all" else None
        if commit:
            conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def make_id(cur, table):
    """Generate an unused numeric ID for one of the app's known tables."""
    if table not in {"customers", "products", "orders"}:
        raise ValueError("Unknown record type.")
    for _ in range(100):
        candidate = secrets.randbelow(900_000) + 100_000
        cur.execute(f"SELECT 1 FROM {table} WHERE id = %s", (candidate,))
        if cur.fetchone() is None:
            return candidate
    raise RuntimeError("Could not generate a unique ID. Please try again.")


class CRMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CRM-Lite | Sign in")
        self.geometry("460x520")
        self.minsize(420, 460)
        self.configure(bg=BG)
        self.current_page = None
        self.authenticated_user = None
        self._setup_style()
        self._show_login()

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                        foreground=INK, rowheight=38, borderwidth=0,
                        font=("Helvetica Neue", 10))
        style.configure("Treeview.Heading", background="#f4f6fa", foreground=MUTED,
                        font=("Helvetica Neue", 9, "bold"), relief="flat", padding=(12, 10))
        style.map("Treeview", background=[("selected", "#e9efff")],
                  foreground=[("selected", INK)])
        style.configure("TCombobox", padding=7, fieldbackground=WHITE)
        style.configure("Vertical.TScrollbar", background=WHITE, troughcolor=WHITE,
                        bordercolor=WHITE, arrowcolor=MUTED)

    def _show_login(self):
        for child in self.winfo_children():
            child.destroy()
        self.title("CRM-Lite | Sign in")
        self.configure(bg=BG)

        card = tk.Frame(self, bg=WHITE, highlightbackground=LINE, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=360)
        tk.Label(card, text="C", bg=ACCENT, fg=WHITE, width=2, height=1,
                 font=("Helvetica Neue", 18, "bold")).pack(pady=(28, 12))
        tk.Label(card, text="Welcome to CRM-Lite", bg=WHITE, fg=INK,
                 font=("Helvetica Neue", 18, "bold")).pack()
        tk.Label(card, text="Sign in with your account to continue.", bg=WHITE, fg=MUTED,
                 font=("Helvetica Neue", 10)).pack(pady=(6, 22))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x", padx=28)
        tk.Label(form, text="Username", bg=WHITE, fg=MUTED,
                 font=("Helvetica Neue", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.login_username = tk.Entry(form, relief="flat", bd=0, bg="#f7f8fb", fg=INK,
                                       insertbackground=INK, font=("Helvetica Neue", 11))
        self.login_username.pack(fill="x", ipady=10, padx=1)
        tk.Label(form, text="Password", bg=WHITE, fg=MUTED,
                 font=("Helvetica Neue", 9, "bold")).pack(anchor="w", pady=(15, 5))
        self.login_password = tk.Entry(form, show="•", relief="flat", bd=0, bg="#f7f8fb",
                                       fg=INK, insertbackground=INK,
                                       font=("Helvetica Neue", 11))
        self.login_password.pack(fill="x", ipady=10, padx=1)
        self.login_password.bind("<Return>", lambda _event: self._login())
        self.login_username.bind("<Return>", lambda _event: self.login_password.focus_set())
        self.login_error = tk.Label(form, text="", bg=WHITE, fg=RED,
                                    font=("Helvetica Neue", 9), wraplength=290, justify="left")
        self.login_error.pack(anchor="w", pady=(9, 0))
        self._button(card, "Sign in", self._login).pack(fill="x", padx=28, pady=(12, 28))
        self.login_username.focus_set()

    def _login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        if not username or not password:
            self.login_error.configure(text="Enter your username and password.")
            return
        try:
            account = db_query(
                "SELECT id, password_hash, is_active, real_name FROM users WHERE username = %s",
                (username,), fetch="one",
            )
        except Exception as exc:
            self.login_error.configure(text=self._error_text(exc))
            return
        if not account or account[2].lower() != "active" or hash_password(password) != account[1]:
            self.login_password.delete(0, "end")
            self.login_error.configure(text="The username or password is incorrect, or the account is inactive.")
            return
        self.authenticated_user = {"id": account[0], "name": account[3], "username": username}
        self.title("CRM-Lite")
        self.geometry("1180x760")
        self.minsize(980, 640)
        for child in self.winfo_children():
            child.destroy()
        self.current_page = "Dashboard"
        self._build_shell()
        self.show_page("Dashboard")

    def _logout(self):
        self.authenticated_user = None
        self.current_page = None
        self.geometry("460x520")
        self.minsize(420, 460)
        self._show_login()

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(27, 36))
        tk.Label(brand, text="C", bg=ACCENT, fg=WHITE, width=2, height=1,
                 font=("Helvetica Neue", 16, "bold")).pack(side="left", padx=(0, 11))
        tk.Label(brand, text="CRM-Lite", bg=SIDEBAR, fg=WHITE,
                 font=("Helvetica Neue", 16, "bold")).pack(side="left")

        tk.Label(self.sidebar, text="WORKSPACE", bg=SIDEBAR, fg="#75829c",
                 font=("Helvetica Neue", 9, "bold")).pack(anchor="w", padx=24, pady=(0, 12))
        self.nav_buttons = {}
        for page, symbol in (("Dashboard", "⌂"), ("Customers", "♙"),
                             ("Orders", "▤"), ("Products", "◇")):
            button = tk.Button(
                self.sidebar, text=f"{symbol}   {page}", anchor="w", relief="flat",
                borderwidth=0, padx=18, pady=12, cursor="hand2",
                font=("Helvetica Neue", 11), command=lambda name=page: self.show_page(name),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[page] = button

        footer = tk.Frame(self.sidebar, bg=SIDEBAR)
        footer.pack(side="bottom", fill="x", padx=22, pady=22)
        tk.Frame(footer, bg="#35415a", height=1).pack(fill="x", pady=(0, 15))
        tk.Label(footer, text="CRM workspace", bg=SIDEBAR, fg=WHITE,
                 font=("Helvetica Neue", 10, "bold")).pack(anchor="w")
        tk.Label(footer, text="Manage your business in one place", bg=SIDEBAR,
                 fg=SIDEBAR_MUTED, font=("Helvetica Neue", 9), wraplength=180,
                 justify="left").pack(anchor="w", pady=(5, 0))
        tk.Button(footer, text="Sign out", command=self._logout, cursor="hand2",
                  relief="flat", borderwidth=0, bg=SIDEBAR, fg=SIDEBAR_MUTED,
                  activebackground=SIDEBAR, activeforeground=WHITE,
                  font=("Helvetica Neue", 9, "bold")).pack(anchor="w", pady=(14, 0))

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

    def show_page(self, page):
        self.current_page = page
        for name, button in self.nav_buttons.items():
            active = name == page
            button.configure(bg="#2a3856" if active else SIDEBAR,
                             fg=WHITE if active else SIDEBAR_MUTED,
                             activebackground="#2a3856", activeforeground=WHITE)
        for child in self.main.winfo_children():
            child.destroy()
        if page == "Dashboard":
            self._dashboard()
        else:
            {"Customers": self._customers_page, "Orders": self._orders_page,
             "Products": self._products_page}[page]()

    def _page_header(self, title, subtitle, button_text=None, command=None):
        top = tk.Frame(self.main, bg=BG)
        top.pack(fill="x", padx=34, pady=(28, 22))
        copy = tk.Frame(top, bg=BG)
        copy.pack(side="left", fill="x", expand=True)
        tk.Label(copy, text=title, bg=BG, fg=INK,
                 font=("Helvetica Neue", 24, "bold")).pack(anchor="w")
        tk.Label(copy, text=subtitle, bg=BG, fg=MUTED,
                 font=("Helvetica Neue", 10)).pack(anchor="w", pady=(5, 0))
        if button_text:
            self._button(top, button_text, command).pack(side="right", anchor="center")

    def _button(self, parent, text, command, secondary=False):
        return tk.Button(parent, text=text, command=command, cursor="hand2",
                         relief="flat", borderwidth=0, padx=16, pady=10,
                         bg=WHITE if secondary else ACCENT,
                         fg=ACCENT if secondary else WHITE,
                         activebackground="#edf1ff" if secondary else ACCENT_DARK,
                         activeforeground=ACCENT if secondary else WHITE,
                         font=("Helvetica Neue", 10, "bold"))

    def _card(self, parent, padx=0, pady=0):
        frame = tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1)
        if padx or pady:
            frame.pack(fill="both", expand=True, padx=padx, pady=pady)
        return frame

    def _table(self, parent, columns, headings, widths=None):
        holder = tk.Frame(parent, bg=WHITE)
        holder.pack(fill="both", expand=True)
        table = ttk.Treeview(holder, columns=columns, show="headings", selectmode="browse")
        for i, (column, heading) in enumerate(zip(columns, headings)):
            table.heading(column, text=heading)
            table.column(column, width=(widths or {}).get(column, 120),
                         anchor="w" if i == 1 else "center", stretch=True)
        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        table.tag_configure("odd", background="#fafbfe")
        return table

    def _safe(self, action):
        try:
            return action()
        except Exception as exc:
            messagebox.showerror("Could not complete action", self._error_text(exc), parent=self)
            return None

    @staticmethod
    def _error_text(exc):
        text = str(exc).strip()
        if "DATABASE_URL" in text or "database" in text.lower() and "connect" in text.lower():
            return "Could not connect to the database. Check DATABASE_URL in your .env file and make sure PostgreSQL is running.\n\n" + text
        return text or "An unexpected database error occurred."

    def _count(self, table):
        row = db_query(f"SELECT COUNT(*) FROM {table}", fetch="one")
        return row[0]

    def _dashboard(self):
        self._page_header("Dashboard", "A quick overview of your business.", "＋  New customer",
                          self._add_customer)
        stats = tk.Frame(self.main, bg=BG)
        stats.pack(fill="x", padx=28)
        definitions = (("Customers", "customers", "♙", ACCENT),
                       ("Orders", "orders", "▤", "#b67816"),
                       ("Products", "products", "◇", GREEN))
        for title, table, symbol, color in definitions:
            card = self._card(stats)
            card.pack(side="left", fill="x", expand=True, padx=6, pady=5)
            row = tk.Frame(card, bg=WHITE)
            row.pack(fill="x", padx=20, pady=18)
            tk.Label(row, text=symbol, bg="#eef2ff", fg=color, width=3, height=1,
                     font=("Helvetica Neue", 15, "bold")).pack(side="right")
            tk.Label(row, text=title, bg=WHITE, fg=MUTED,
                     font=("Helvetica Neue", 10)).pack(anchor="w")
            value = tk.Label(row, text="—", bg=WHITE, fg=INK,
                             font=("Helvetica Neue", 25, "bold"))
            value.pack(anchor="w", pady=(7, 0))
            self._safe(lambda v=value, t=table: v.configure(text=self._count(t)))

        section = self._card(self.main, padx=34, pady=20)
        section.pack_configure(fill="both", expand=True)
        title_row = tk.Frame(section, bg=WHITE)
        title_row.pack(fill="x", padx=20, pady=(18, 12))
        tk.Label(title_row, text="Recent orders", bg=WHITE, fg=INK,
                 font=("Helvetica Neue", 14, "bold")).pack(side="left")
        self._button(title_row, "View orders", lambda: self.show_page("Orders"), True).pack(side="right")
        table = self._table(section, ("id", "customer", "status", "price"),
                            ("ORDER", "CUSTOMER", "STATUS", "TOTAL"),
                            {"id": 100, "customer": 260, "status": 150, "price": 130})
        table.pack_configure(padx=10, pady=(0, 12))
        rows = self._safe(lambda: db_query(
            "SELECT o.id, c.l_name, o.status, o.price FROM orders o "
            "LEFT JOIN customers c ON c.id = o.customer_id ORDER BY o.id DESC LIMIT 8"
        ))
        if rows:
            for index, row in enumerate(rows):
                table.insert("", "end", values=(f"#{row[0]}", row[1] or "—", row[2],
                                                  f"€{row[3]:,.2f}" if row[3] is not None else "—"),
                             tags=("odd" if index % 2 else "",))
        elif rows == []:
            table.insert("", "end", values=("No orders yet", "Create an order to see it here", "", ""))

    def _search_bar(self, parent, variable, placeholder="Search"):
        holder = tk.Frame(parent, bg=WHITE, highlightbackground=LINE, highlightthickness=1)
        tk.Label(holder, text="⌕", bg=WHITE, fg=MUTED,
                 font=("Helvetica Neue", 14)).pack(side="left", padx=(11, 2))
        entry = tk.Entry(holder, textvariable=variable, relief="flat", bd=0,
                         bg=WHITE, fg=INK, insertbackground=INK,
                         font=("Helvetica Neue", 10), width=28)
        entry.pack(side="left", padx=6, pady=10)
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda _e: entry.delete(0, "end") if entry.get() == placeholder else None)
        return holder

    def _customers_page(self):
        self._page_header("Customers", "View and manage your customer relationships.",
                          "＋  Add customer", self._add_customer)
        controls = tk.Frame(self.main, bg=BG)
        controls.pack(fill="x", padx=34, pady=(0, 12))
        self.customer_search = tk.StringVar()
        search = self._search_bar(controls, self.customer_search, "Search customers")
        search.pack(side="left")
        self.customer_search.trace_add("write", lambda *_: self._refresh_customers())
        card = self._card(self.main, padx=34, pady=8)
        self.customer_table = self._table(card,
            ("id", "name", "type", "phone", "status", "created"),
            ("ID", "CUSTOMER", "TYPE", "PHONE", "STATUS", "CREATED"),
            {"id": 90, "name": 210, "type": 120, "phone": 150, "status": 110, "created": 150})
        self.customer_table.bind("<Double-1>", lambda _e: self._change_customer_status())
        bottom = tk.Frame(card, bg=WHITE)
        bottom.pack(fill="x", padx=16, pady=12)
        tk.Label(bottom, text="Double-click a customer to change their status.", bg=WHITE,
                 fg=MUTED, font=("Helvetica Neue", 9)).pack(side="left")
        self._button(bottom, "Change status", self._change_customer_status, True).pack(side="right")
        self._refresh_customers()

    def _refresh_customers(self):
        if not hasattr(self, "customer_table") or not self.customer_table.winfo_exists():
            return
        for item in self.customer_table.get_children():
            self.customer_table.delete(item)
        query = self.customer_search.get().strip() if hasattr(self, "customer_search") else ""
        rows = self._safe(lambda: db_query(
            "SELECT id, f_name, l_name, type, phone, status, created_at FROM customers "
            "WHERE (%s = '' OR CONCAT_WS(' ', f_name, l_name, phone, vat, id::text) ILIKE %s) "
            "ORDER BY id DESC", (query, f"%{query}%")))
        if rows:
            for index, row in enumerate(rows):
                created = str(row[6])[:10] if row[6] else "—"
                self.customer_table.insert("", "end", values=(row[0],
                    " ".join(part for part in (row[1], row[2]) if part) or "—",
                    row[3], row[4], row[5], created), tags=("odd" if index % 2 else "",))

    def _add_customer(self):
        fields = (("First name", "first", ""), ("Last name *", "last", ""),
                  ("Phone *", "phone", ""), ("Customer type", "type", "Individual"),
                  ("VAT number", "vat", ""), ("Address", "address", ""))
        values = self._form_dialog("Add customer", fields,
                                   ("Individual", "Business"), "Create customer")
        if values is None:
            return
        if not values["last"].strip() or not values["phone"].strip():
            messagebox.showwarning("Missing details", "Last name and phone are required.", parent=self)
            return

        def save():
            conn, cur = connect_db()
            try:
                customer_id = make_id(cur, "customers")
                now = datetime.now().isoformat(sep=" ", timespec="seconds")
                cur.execute("INSERT INTO customers (id,type,f_name,l_name,vat,phone,address,orders,created_at,last_modified,status) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (customer_id, values["type"], values["first"].strip() or None,
                             values["last"].strip(), values["vat"].strip() or None,
                             values["phone"].strip(), values["address"].strip() or None,
                             [], now, now, "active"))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            self._refresh_customers()
            messagebox.showinfo("Customer added", f"Customer #{customer_id} was added.", parent=self)

        self._safe(save)

    def _change_customer_status(self):
        selection = self.customer_table.selection() if hasattr(self, "customer_table") else ()
        if not selection:
            messagebox.showinfo("Select a customer", "Choose a customer first.", parent=self)
            return
        row = self.customer_table.item(selection[0], "values")
        new_status = "inactive" if row[4].lower() == "active" else "active"
        result = self._safe(lambda: db_query("UPDATE customers SET status = %s, last_modified = %s WHERE id = %s",
                                             (new_status, datetime.now().isoformat(sep=" ", timespec="seconds"),
                                              int(row[0])), fetch="none", commit=True))
        if result is None:
            # UPDATE has no result by design; _safe also returns None on errors.
            try:
                self._refresh_customers()
            except Exception:
                pass

    def _orders_page(self):
        self._page_header("Orders", "Track customer orders and their status.",
                          "＋  Create order", self._add_order)
        card = self._card(self.main, padx=34, pady=8)
        self.order_table = self._table(card, ("id", "customer", "items", "status", "price"),
                                       ("ORDER", "CUSTOMER", "PRODUCTS", "STATUS", "TOTAL"),
                                       {"id": 100, "customer": 200, "items": 250, "status": 140, "price": 130})
        self.order_table.bind("<Double-1>", lambda _e: self._change_order_status())
        bottom = tk.Frame(card, bg=WHITE)
        bottom.pack(fill="x", padx=16, pady=12)
        tk.Label(bottom, text="Double-click an order to update its status.", bg=WHITE,
                 fg=MUTED, font=("Helvetica Neue", 9)).pack(side="left")
        self._button(bottom, "Update status", self._change_order_status, True).pack(side="right")
        self._refresh_orders()

    def _refresh_orders(self):
        if not hasattr(self, "order_table") or not self.order_table.winfo_exists():
            return
        for item in self.order_table.get_children():
            self.order_table.delete(item)
        rows = self._safe(lambda: db_query(
            "SELECT o.id, c.l_name, o.products, o.status, o.price FROM orders o "
            "LEFT JOIN customers c ON c.id = o.customer_id ORDER BY o.id DESC"))
        if rows:
            for index, row in enumerate(rows):
                items = ", ".join(str(value) for value in (row[2] or [])) or "—"
                self.order_table.insert("", "end", values=(f"#{row[0]}", row[1] or "—", items,
                    row[3], f"€{row[4]:,.2f}" if row[4] is not None else "—"),
                    tags=("odd" if index % 2 else "",))

    def _add_order(self):
        data = self._safe(lambda: (
            db_query("SELECT id, COALESCE(f_name || ' ', '') || l_name FROM customers WHERE status = 'active' ORDER BY l_name"),
            db_query("SELECT id, name, price, stock FROM products ORDER BY name")))
        if not data:
            return
        customers, products = data
        if not customers:
            messagebox.showinfo("No active customers", "Add an active customer before creating an order.", parent=self)
            return
        if not products:
            messagebox.showinfo("No products", "Add a product before creating an order.", parent=self)
            return
        dialog = tk.Toplevel(self)
        dialog.title("Create order")
        dialog.configure(bg=WHITE)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        body = tk.Frame(dialog, bg=WHITE, padx=24, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Create an order", bg=WHITE, fg=INK,
                 font=("Helvetica Neue", 17, "bold")).pack(anchor="w", pady=(0, 16))
        tk.Label(body, text="Customer", bg=WHITE, fg=MUTED).pack(anchor="w")
        customer_map = {f"{name}  ·  #{id}": id for id, name in customers}
        customer_var = tk.StringVar(value=next(iter(customer_map)))
        ttk.Combobox(body, textvariable=customer_var, values=list(customer_map),
                     state="readonly", width=45).pack(fill="x", pady=(5, 14))
        tk.Label(body, text="Products  ·  hold ⌘ / Ctrl to select more than one", bg=WHITE,
                 fg=MUTED).pack(anchor="w")
        product_list = tk.Listbox(body, selectmode="extended", height=min(9, max(4, len(products))),
                                  width=55, bg="#fbfcff", fg=INK, relief="flat",
                                  highlightbackground=LINE, font=("Helvetica Neue", 10),
                                  selectbackground="#e5ebff", selectforeground=INK,
                                  activestyle="none", exportselection=False)
        product_list.pack(fill="x", pady=(6, 6))
        product_labels = [f"{name}  ·  €{price:,.2f}  ·  stock {stock}  ·  #{id}"
                          for id, name, price, stock in products]
        for label in product_labels:
            product_list.insert("end", label)
        total_label = tk.Label(body, text="Select products to see the total", bg=WHITE,
                               fg=MUTED, font=("Helvetica Neue", 10, "bold"))
        total_label.pack(anchor="w", pady=(0, 14))

        def update_total(_event=None):
            total = sum((Decimal(str(products[i][2])) for i in product_list.curselection()), Decimal("0"))
            total_label.configure(text=f"Order total: €{total:,.2f}" if product_list.curselection()
                                  else "Select products to see the total", fg=INK)

        product_list.bind("<<ListboxSelect>>", update_total)
        actions = tk.Frame(body, bg=WHITE)
        actions.pack(fill="x")
        self._button(actions, "Cancel", dialog.destroy, True).pack(side="right", padx=(8, 0))

        def save_order():
            picked = product_list.curselection()
            if not picked:
                messagebox.showwarning("Select products", "Choose at least one product.", parent=dialog)
                return
            chosen = [products[i] for i in picked]
            total = sum((Decimal(str(row[2])) for row in chosen), Decimal("0"))
            conn, cur = connect_db()
            try:
                order_id = make_id(cur, "orders")
                customer_id = customer_map[customer_var.get()]
                cur.execute("INSERT INTO orders (id,status,customer_id,products,price) VALUES (%s,%s,%s,%s,%s)",
                            (order_id, "pending", customer_id, [str(row[0]) for row in chosen], total))
                cur.execute("UPDATE customers SET orders = array_append(COALESCE(orders, ARRAY[]::text[]), %s), last_modified = %s WHERE id = %s",
                            (str(order_id), datetime.now().isoformat(sep=" ", timespec="seconds"), customer_id))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            dialog.destroy()
            self._refresh_orders()
            messagebox.showinfo("Order created", f"Order #{order_id} was created.", parent=self)

        self._button(actions, "Create order", lambda: self._safe(save_order)).pack(side="right")

    def _change_order_status(self):
        selection = self.order_table.selection() if hasattr(self, "order_table") else ()
        if not selection:
            messagebox.showinfo("Select an order", "Choose an order first.", parent=self)
            return
        row = self.order_table.item(selection[0], "values")
        choice = simpledialog.askstring("Update order status", "Enter a status (pending, processing, completed, cancelled):",
                                        initialvalue=row[3], parent=self)
        if choice is None:
            return
        new_status = choice.strip().lower()
        if new_status not in {"pending", "processing", "completed", "cancelled"}:
            messagebox.showwarning("Invalid status", "Choose pending, processing, completed, or cancelled.", parent=self)
            return
        self._safe(lambda: db_query("UPDATE orders SET status = %s WHERE id = %s",
                                    (new_status, int(str(row[0]).lstrip("#"))), fetch="none", commit=True))
        self._refresh_orders()

    def _products_page(self):
        self._page_header("Products", "Keep your catalogue and stock levels up to date.",
                          "＋  Add product", self._add_product)
        card = self._card(self.main, padx=34, pady=8)
        self.product_table = self._table(card,
            ("id", "name", "price", "stock", "variants", "description"),
            ("ID", "PRODUCT", "PRICE", "STOCK", "VARIANTS", "DESCRIPTION"),
            {"id": 90, "name": 190, "price": 110, "stock": 90, "variants": 180, "description": 260})
        bottom = tk.Frame(card, bg=WHITE)
        bottom.pack(fill="x", padx=16, pady=12)
        tk.Label(bottom, text="Select a product to add stock.", bg=WHITE, fg=MUTED,
                 font=("Helvetica Neue", 9)).pack(side="left")
        self._button(bottom, "Restock", self._restock_product, True).pack(side="right")
        self._refresh_products()

    def _refresh_products(self):
        if not hasattr(self, "product_table") or not self.product_table.winfo_exists():
            return
        for item in self.product_table.get_children():
            self.product_table.delete(item)
        rows = self._safe(lambda: db_query("SELECT id,name,price,stock,variants,descr FROM products ORDER BY name"))
        if rows:
            for index, row in enumerate(rows):
                variants = ", ".join(str(value) for value in (row[4] or [])) or "—"
                descr = row[5] or "—"
                self.product_table.insert("", "end", values=(row[0], row[1], f"€{row[2]:,.2f}",
                    "Not tracked" if row[3] == -1 else row[3], variants, descr),
                    tags=("odd" if index % 2 else "",))

    def _add_product(self):
        fields = (("Product name *", "name", ""), ("Price *", "price", ""),
                  ("Initial stock (-1 = not tracked)", "stock", "0"),
                  ("Variants (comma separated)", "variants", ""), ("Description", "description", ""))
        values = self._form_dialog("Add product", fields, None, "Create product")
        if values is None:
            return
        try:
            price = Decimal(values["price"])
            stock = int(values["stock"])
            if price < 0 or stock < -1:
                raise ValueError
        except (ValueError, InvalidOperation):
            messagebox.showwarning("Check product details", "Enter a valid price and stock value.", parent=self)
            return
        if not values["name"].strip():
            messagebox.showwarning("Missing product name", "Product name is required.", parent=self)
            return

        def save():
            conn, cur = connect_db()
            try:
                product_id = make_id(cur, "products")
                variants = [part.strip() for part in values["variants"].split(",") if part.strip()]
                cur.execute("INSERT INTO products (id,name,price,variants,descr,stock) VALUES (%s,%s,%s,%s,%s,%s)",
                            (product_id, values["name"].strip(), price, variants,
                             values["description"].strip() or None, stock))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            self._refresh_products()
            messagebox.showinfo("Product added", f"{values['name'].strip()} was added to your catalogue.", parent=self)

        self._safe(save)

    def _restock_product(self):
        selection = self.product_table.selection() if hasattr(self, "product_table") else ()
        if not selection:
            messagebox.showinfo("Select a product", "Choose a product first.", parent=self)
            return
        row = self.product_table.item(selection[0], "values")
        amount = simpledialog.askinteger("Restock product", f"How many units should be added to {row[1]}?",
                                         minvalue=1, parent=self)
        if amount is None:
            return
        self._safe(lambda: db_query("UPDATE products SET stock = stock + %s WHERE id = %s AND stock >= 0",
                                    (amount, int(row[0])), fetch="none", commit=True))
        self._refresh_products()

    def _form_dialog(self, title, fields, options, submit_text):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=WHITE)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        body = tk.Frame(dialog, bg=WHITE, padx=24, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text=title, bg=WHITE, fg=INK,
                 font=("Helvetica Neue", 17, "bold")).pack(anchor="w", pady=(0, 16))
        variables = {}
        for label, key, default in fields:
            tk.Label(body, text=label, bg=WHITE, fg=MUTED,
                     font=("Helvetica Neue", 9, "bold")).pack(anchor="w", pady=(7, 4))
            variable = tk.StringVar(value=default)
            variables[key] = variable
            if key == "type" and options:
                ttk.Combobox(body, textvariable=variable, values=options,
                             state="readonly", width=40).pack(fill="x")
            else:
                tk.Entry(body, textvariable=variable, relief="flat", bd=0,
                         bg="#f7f8fb", fg=INK, insertbackground=INK,
                         font=("Helvetica Neue", 10)).pack(fill="x", ipady=9, padx=1)
        actions = tk.Frame(body, bg=WHITE)
        actions.pack(fill="x", pady=(20, 0))
        outcome = {"values": None}

        def submit():
            outcome["values"] = {key: value.get() for key, value in variables.items()}
            dialog.destroy()

        self._button(actions, "Cancel", dialog.destroy, True).pack(side="right", padx=(8, 0))
        self._button(actions, submit_text, submit).pack(side="right")
        dialog.update_idletasks()
        dialog.geometry(f"{max(dialog.winfo_reqwidth(), 390)}x{dialog.winfo_reqheight()}")
        self.wait_window(dialog)
        return outcome["values"]


if __name__ == "__main__":
    CRMApp().mainloop()
