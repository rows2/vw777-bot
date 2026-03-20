from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("TOKEN")

users = {}

def teclado():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Seguro", callback_data="seguro")],
        [InlineKeyboardButton("💣 Mina", callback_data="mina")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = 0
    await update.message.reply_text("🎮 Mines Asistente", reply_markup=teclado())

def decision(tiros):
    if tiros <= 1:
        return "👉 Sigue"
    elif tiros == 2:
        return "⚠️ Riesgo, decide"
    else:
        return "🛑 RETÍRATE YA"

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in users:
        users[user_id] = 0

    if query.data == "seguro":
        users[user_id] += 1
        tiros = users[user_id]
        mensaje = f"✅ Aciertos: {tiros}\n{decision(tiros)}"

    elif query.data == "mina":
        users[user_id] = 0
        mensaje = "💣 Perdiste — reinicio"

    await query.answer()
    await query.edit_message_text(mensaje, reply_markup=teclado())

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(botones))

app.run_polling()
