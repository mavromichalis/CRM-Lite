from ..models.user import User
from ..db.connection import connect_db
from ..utils.id_generator import generate_id
from ..utils.hasher import hash
from ..models.errors import AppError,PostgresError

def check_username_avail(username):
    conn , cur = connect_db()
    try:
        cur.execute("SELECT is_active FROM users WHERE username = %s",(username,))
        res = cur.fetchone()
        if res:
            return False #Taken
        else:
            return True #Free
    except AppError:
        return False
    except PostgresError:
        conn.rollback()
        return False
    finally: conn.close()

def create_user(username,password,real_name,role,is_active):
    conn , cur = connect_db()
    id = generate_id('users')
    try:
        if check_username_avail(username) == False:
            raise AppError('Username Taken.')
        cur.execute(
            """
            INSERT INTO users (id,username,password_hash,real_name,role,is_active) VALUES (%s,%s,%s,%s,%s,%s)
            """
        ,(id,username,hash(password),real_name,role,is_active))
        conn.commit()
        return User(id,username,hash(password),real_name,role,is_active)
    except AppError as e:
        conn.rollback()
        return e
    finally:
        conn.close()
    