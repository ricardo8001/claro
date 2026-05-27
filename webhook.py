from flask import Flask, request
import json
from users import UserManager

app = Flask(__name__)
user_manager = UserManager()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("=== WEBHOOK RECEBIDO ===")
        print(json.dumps(data, indent=2))

        if data.get("status") == "COMPLETO":
            transaction_id = str(data.get("transactionId", ""))
            value = data.get("value", 0) / 100

            if "dep_" in transaction_id:
                user_id = int(transaction_id.split("_")[1])
                novo_saldo = user_manager.adicionar_saldo(user_id, value)
                print(f"✅ SALDO ADICIONADO → User {user_id} + R${value:.2f} | Total: R${novo_saldo:.2f}")
        return {"status": "success"}, 200
    except Exception as e:
        print(f"Erro webhook: {e}")
        return {"status": "error"}, 500

@app.route('/')
def home():
    return "Webhook MisticPay Online!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
  
