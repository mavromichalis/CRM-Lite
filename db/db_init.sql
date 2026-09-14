CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    real_name TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active TEXT NOT NULL default='active'
);

CREATE TABLE logs(
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL
);

CREATE TABLE customers(
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    f_name TEXT,
    l_name TEXT NOT NULL,
    vat TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    address TEXT,
    orders TEXT[],
    created_at TEXT NOT NULL,
    last_modified TEXT,
    status TEXT NOT NULL
);

CREATE TABLE orders(
    id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    products = TEXT[],
    price DECIMAL(10,2)
);

CREATE TABLE products(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    variants TEXT [],
    descr TEXT,
    stock INTEGER NOT NULL
);