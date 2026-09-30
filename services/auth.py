from ..db.connection import connect_db
from ..models.user import User
from ..utils.hasher import hash
from ..utils.id_generator import generate_id
from ..utils.logs import generate_logs
from ..models.errors import InactiveAccount,WrongPassword,UsernameTaken,UserDoesNotExist,AppError,PostgresError
from .users import check_username_avail

def attempt_auth(username,password):
    hashed_pwd = hash(password)
    conn , cur = connect_db()
    try:
        cur.execute(
            """
            SELECT is_active,id,password_hash FROM users WHERE username = %s
            """
        ,(username,))
        res = cur.fetchone()
        if not res:
            raise UserDoesNotExist
        if hashed_pwd != res[2]:
            raise WrongPassword
        if res[0] == 'active':
            generate_logs(username,'Logged in.')
            return generate_user_object(res[1])
        else:
            raise InactiveAccount
    except UserDoesNotExist or WrongPassword or InactiveAccount or AppError as e:
        return {
            "Code":e.code,
            "Message":e.message,
            "Status Code":e.status_code
        }
    except PostgresError as e:
        conn.rollback()
        return e.message
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
            raise UserDoesNotExist
    except UserDoesNotExist or AppError:
        return None
    except PostgresError: 
        conn.rollback()
        return None
    finally:
        conn.close()

def create_user(username,password,real_name,role,is_active):
    conn , cur = connect_db()
    try:
        if check_username_avail(username) == False:
            raise UsernameTaken
        id = generate_id('users')
        cur.execute(
            """
            INSERT INTO users (id,username,password_hash,real_name,role,is_active) VALUES (%s,%s,%s,%s,%s,%s)
            """
        ,(id,username,hash(password),real_name,role,is_active))
        conn.commit()
        generate_logs(username,'User signed up.')
        return generate_user_object(id)
    except UsernameTaken or AppError as e:
            return {
            "Code":e.code,
            "Message":e.message,
            "Status Code":e.status_code
        }
    except PostgresError:
        conn.rollback()
        return None
    finally:
        conn.close()

