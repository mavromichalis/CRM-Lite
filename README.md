# CRM-Lite

> ⚠️ **WORK IN PROGRESS — not runnable end-to-end yet.** Several crash bugs from the initial version have been fixed, but the project still can't be imported or run as-is (see [Known Issues](#known-issues)). Do not use this for anything real yet.

A lightweight CRM backend in Python, backed by PostgreSQL. Manages customers, orders, products, and users.

## Structure

```
CRM-Lite/
├── db/
│   ├── connection.py      # Postgres connection via psycopg2 + python-dotenv
│   ├── db_init.sql        # Schema (users, logs, customers, orders, products)
│   └── .env.example       # Template for DATABASE_URL
├── models/
│   ├── customer.py
│   ├── order.py           # stub only — no persistence methods yet
│   ├── product.py
│   └── user.py
├── services/
│   ├── auth.py            # login / signup
│   └── orders.py          # create_order() — has known bugs, see below
└── utils/
    ├── hasher.py           # password hashing
    ├── id_generator.py     # random numeric ID generator
    └── logs.py             # activity logging
```

## Setup

**Blocked by the first item under Known Issues — there is no way to actually import or run this yet.** Once that's resolved, the intended setup is:

1. Create a PostgreSQL database.
2. Copy `db/.env.example` to `db/.env` and set `DATABASE_URL`.
3. Run `db/db_init.sql` against your database to create the schema.
4. Install dependencies: `psycopg2`, `python-dotenv`.

## Known issues

### Blocking

- **No `__init__.py` anywhere.** Every module uses relative imports (`from ..db.connection import ...`) but there's no package structure to support them and no entrypoint script. Nothing can currently be imported or run.

### Bugs

- **`create_order()` in `services/orders.py` passes a non-tuple to `cur.execute()`:** `(product)` is just `product` in parentheses, not a 1-tuple — needs `(product,)`. As written this raises an error on every call.
- **`create_order()` adds a row tuple instead of a value:** `price += res` adds the whole `fetchone()` result tuple to `price`, not the price itself. Needs `price += res[0]`.
- Broad `except Exception` blocks throughout (`auth.py`, `orders.py`, `customer.py`, `product.py`, `id_generator.py`) silently swallow all errors with no logging, which will make the two bugs above (and anything else) hard to diagnose once this runs.

### Incomplete

- **`models/order.py` has no persistence methods** — only `__init__`. No way to create, update status, or otherwise persist an `Order` from the model itself (order creation currently lives entirely in `services/orders.py`).
- **`attempt_auth()` has no session/token mechanism** — returns a raw `(status, id)` tuple with nothing a caller could use to maintain an authenticated session.
- **`db/.env.example` is not a usable template:** `DATABASE_URL = Enter URL here` reads as an instruction rather than an example value.

### Fixed since the last version

- `hasher.py` — `hash()` no longer references an undefined variable.
- `logs.py` — `generate_logs()` now calls `datetime.now()` correctly and returns the right id.
- `services/auth.py` — `create_user()` no longer calls the nonexistent `cur.lastrowid()`.
- `models/customer.py` — `change_status()` now updates the correct `customers` table.
- `models/user.py` — `get_info()` now references the correct `real_name` attribute.
- `db/db_init.sql` — the invalid syntax in the `orders` table definition is fixed and the schema now parses.

## Roadmap

- [ ] Add `__init__.py` files and a proper entrypoint
- [ ] Fix the two new bugs in `create_order()`
- [ ] Build out `models/order.py`
- [ ] Add a session/token mechanism to auth
- [ ] Replace silent broad excepts with real error logging
- [ ] Fix `.env.example`
- [ ] Add tests

## License

Not yet decided.
