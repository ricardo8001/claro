import json
import os
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_users(self):
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def get_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.users:
            self.users[user_id] = {"saldo": 0.0, "recargas_feitas": 0, "ultima_atividade": datetime.now().isoformat()}
            self.save_users()
        return self.users[user_id]

    def adicionar_saldo(self, user_id, valor):
        user = self.get_user(user_id)
        user["saldo"] += round(float(valor), 2)
        user["ultima_atividade"] = datetime.now().isoformat()
        self.save_users()
        return user["saldo"]
