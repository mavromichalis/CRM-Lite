# CRM-Lite

> ⚠️ **WORK IN PROGRESS — not functional yet.** This project is in early development. Several core paths (auth, logging, database init) are currently broken. See [Known Issues](#known-issues) before trying to run it. Do not use this for anything real yet.

A lightweight CRM backend in Python, backed by PostgreSQL. Manages customers, orders, products, and users.

## Structure

```
CRM-Lite/
├── db/
│   ├── connection.py      # Postgres connection via psycopg2 + python-dotenv
│   ├── db_init.sql        # Schema (customers, orders, products, users)
│   └── .env.example       # Template for DATABASE_URL
├── models/
│   ├── customer.py
│   ├── order.py           # stub only — no persistence methods yet
│   ├── product.py
│   └── user.py
├── services/
│   ├── auth.py            # login / signup
│   └── orders.py          # currently empty
└── utils/
    ├── hasher.py           # password hashing
    ├── id_generator.py     # random numeric ID generator
    └── logs.py             # activity logging
```

## Setup

**This will not currently run end-to-end — see [Known Issues](#known-issues).** Once the blocking issues below are fixed, the intended setup is:

1. Create a PostgreSQL database.
2. Copy `db/.env.example` to `db/.env` and set `DATABASE_URL`.
3. Run `db/db_init.sql` against your database to create the schema.
4. Install dependencies: `psycopg2`, `python-dotenv`.

There is currently no entrypoint script (e.g. `main.py`) and no package `__init__.py` files, so the modules cannot be imported or run as-is.

## Known issues

The following are tracked as GitHub issues and block basic functionality:

- **No `__init__.py` anywhere** — every module uses relative imports (`from ..db.connection import ...`) with no package structure to support them. Nothing can currently be imported or run.
- **`db_init.sql` does not parse** — invalid syntax in the `orders` and `users` table definitions (stray `=`, invalid `DEFAULT` syntax). The schema cannot be created as-is.
- **`hash()` in `utils/hasher.py` throws `NameError`** — references an undefined variable. Breaks login and signup.
- **`generate_logs()` in `utils/logs.py` throws `AttributeError`** and returns the wrong value even when it doesn't crash.
- **`create_user()` in `services/auth.py`** calls a psycopg2 cursor method (`lastrowid`) that doesn't exist.
- **`Customer.change_status()`** updates a table (`clients`) that isn't in the schema (`customers`).
- **`User.get_info()`** references an attribute (`self.name`) that doesn't exist (`self.real_name`).
- **`services/orders.py` is empty** — no order-related service logic exists yet.
- **`models/order.py` has no persistence methods** — only `__init__`.
- Broad `except Exception` blocks throughout swallow all errors silently, with no logging — makes debugging any of the above much harder than it needs to be.

Full list with fix suggestions is in the repo's Issues tab.

## Roadmap

- [ ] Add `__init__.py` files and a proper entrypoint
- [ ] Fix `db_init.sql` so the schema actually creates
- [ ] Fix the crash bugs in `hasher.py`, `logs.py`, `auth.py`, `customer.py`, `user.py`
- [ ] Build out `services/orders.py` and `models/order.py`
- [ ] Add a session/token mechanism to auth
- [ ] Replace silent broad excepts with real error logging
- [ ] Add tests

## License

Not yet decided.