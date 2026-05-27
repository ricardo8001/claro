import os
import time
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ===================== USER MANAGER =====================
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

# ===================== MISTIC PAY =====================
class MisticPay:
    def __init__(self):
        self.ci = "ci_rfngefr055yllf7"
        self.cs = "cs_s2xua7aqqxwiqzo80dsxv2vhr"
        self.webhook_url = os.getenv("WEBHOOK_URL", "https://seu-bot.onrender.com/webhook")

    def criar_pix(self, amount, payer_name, transaction_id):
        import requests
        headers = {'ci': self.ci, 'cs': self.cs, 'Content-Type': 'application/json'}
        data = {
            "amount": float(amount),
            "payerName": payer_name,
            "payerDocument": "00000000000",
            "transactionId": transaction_id,
            "description": "Depósito Bot Claro",
            "projectWebhook": self.webhook_url
        }
        try:
            r = requests.post('https://api.misticpay.com/api/transactions/create', headers=headers, json=data, timeout=20)
            return r.json()
        except:
            return None

# ===================== GLOBAIS =====================
user_manager = UserManager()
misticpay = MisticPay()
user_sessions = {}

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = user_manager.get_user(user_id)
    nome = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("👤 Meu Perfil", callback_data="perfil")],
        [InlineKeyboardButton("💰 Adicionar Saldo", callback_data="add_saldo")],
        [InlineKeyboardButton("📱 Fazer Recarga Claro", callback_data="iniciar_recarga")]
    ]

    await update.message.reply_text(
        f"👋 *Bem-vindo, {nome}*\n\n💰 *Saldo:* R$ {user['saldo']:.2f}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data

    if data == "add_saldo":
        await query.edit_message_text("💰 Digite o valor (mínimo R$15,00):", parse_mode='Markdown')
        user_sessions[user_id] = {'step': 'waiting_deposit'}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_sessions or user_sessions[user_id].get('step') != 'waiting_deposit':
        await update.message.reply_text("Use /menu")
        return

    try:
        amount = float(re.sub(r'[^0-9.,]', '', text).replace(',', '.'))
        if amount < 15:
            await update.message.reply_text("❌ Mínimo R$15,00")
            return

        transaction_id = f"dep_{user_id}_{int(time.time())}"
        response = misticpay.criar_pix(amount, update.effective_user.first_name, transaction_id)

        if response and 'data' in response:
            await update.message.reply_text("✅ PIX gerado! Pague e o saldo será adicionado automaticamente.")
        else:
            await update.message.reply_text("❌ Erro ao gerar PIX.")
    except:
        await update.message.reply_text("❌ Valor inválido. Digite apenas o número.")

def main():
    TOKEN = "7748457693:AAHGW30nEHdbGBI6pCZNdQPzCUgUPiUfO4k"
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", menu_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 BOT INICIADO NO RENDER")
    application.run_polling()

if __name__ == "__main__":
    main()
