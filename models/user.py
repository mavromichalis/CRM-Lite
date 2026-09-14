from ..db.connection import connect_db
from ..utils.logs import generate_logs

class User:
    def __init__(self,id,username,password,real_name,role,is_active):
        self.id = id
        self.username = username
        self.password = password
        self.real_name = real_name
        self.role = role
        self.is_active = is_active

    def get_user_logs(self):
        conn,cur = connect_db()
        try:
            cur.execute(
                """
                SELECT * FROM logs WHERE user_id = %s
                """
            ,(self.id,))
            res = cur.fetchall()
            generate_logs(self.id,'Fetched logs.')
            return res
        finally:
            conn.close()

    def get_info(self):
        return{
            "User ID: ":self.id,
            "Username: ":self.username,
            "Name: ":self.name,
            "Role: ":self.role,
            "Activity Status: ":self.is_active
        }

    
    