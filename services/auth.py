from ..db.connection import connect_db
from ..models.user import User
from ..utils.hasher import hash
from ..utils.id_generator import generate_id
from ..utils.logs import generate_logs

def attempt_auth(username,password):
    hashed_pwd = hash(password)
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT is_active,id FROM users WHERE username = %s AND password_hash = %s
            """
        ,(username,hashed_pwd))
        res = cur.fetchone()
        if res[0] == 'active':
            generate_logs(username,'Logged in.')
            return res[0],res[1]
        else:
            raise Exception
    except Exception:
        return None,None
    finally:
        conn.close()

def generate_user_object(id):
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT * FROM users WHERE id = %s
            """
        ,(id,))
        res = cur.fetchone()
        if res:
            return User(id,res[1],res[2],res[3],res[4],res[5])
        else:
            raise Exception
    except Exception:
        return None
    finally:
        conn.close()

def create_user(username,password,real_name,role,is_active):
    conn , cur = connect_db()
    try:
        id = generate_id('users')
        cur.execute(
            """
            INSERT INTO users (id,username,password_hash,real_name,role,is_active) VALUES (%s,%s,%s,%s,%s,%s)
            """
        ,(id,username,hash(password),real_name,role,is_active))
        conn.commit()
        generate_logs(username,'User signed up.')
        return generate_user_object(id)
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()