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