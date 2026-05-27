from flask import Flask, request
import json
from users import UserManager

app = Flask(__name__)
user_manager = UserManager()

@app.route('/webhook', methods=['POST'])
def misticpay_webhook():
    try:
        data = request.get_json()
        
        print("="*50)
        print("🔥 WEBHOOK RECEBIDO DO MISTICPAY")
        print(json.dumps(data, indent=2))
        print("="*50)

        # Verifica se o pagamento foi completado
        if data.get("status") == "COMPLETO" and data.get("transactionType") == "DEPOSITO":
            transaction_id = str(data.get("transactionId", ""))
            value = float(data.get("value", 0)) / 100  # converte centavos para reais

            if transaction_id.startswith("dep_"):
                try:
                    user_id = int(transaction_id.split("_")[1])
                    novo_saldo = user_manager.adicionar_saldo(user_id, value)
                    
                    print(f"✅ SUCESSO! Saldo adicionado para usuário {user_id}")
                    print(f"   Valor: R${value:.2f} | Saldo atual: R${novo_saldo:.2f}")
                    
                except Exception as e:
                    print(f"❌ Erro ao processar user_id: {e}")
            else:
                print("⚠️ Transaction ID não possui formato esperado (dep_)")
        else:
            print("ℹ️ Status não é COMPLETO ou não é DEPÓSITO")

        return {"status": "success"}, 200

    except Exception as e:
        print(f"❌ ERRO NO WEBHOOK: {e}")
        return {"status": "error"}, 500


@app.route('/')
def home():
    return """
    <h1>✅ Webhook MisticPay Online</h1>
    <p>Bot: <strong>botezap.onrender.com</strong></p>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
