import random
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")  # Railway usa esto

DB_FILE = "db.json"

# ------------------ BASE DE DATOS ------------------

def cargar_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

usuarios = cargar_db()

# ------------------ FUNCIONES ------------------

def crear_usuario(user_id):
    if str(user_id) not in usuarios:
        usuarios[str(user_id)] = {
            "saldo": 100,
            "ganadas": 0,
            "perdidas": 0
        }
        guardar_db(usuarios)

def generar_tablero():
    tablero = []
    minas = random.sample(range(9), 3)  # 3 minas
    for i in range(9):
        if i in minas:
            tablero.append("💣")
        else:
            tablero.append("💎")
    return tablero

def teclado_tablero():
    botones = []
    for i in range(3):
        fila = []
        for j in range(3):
            pos = i * 3 + j
            fila.append(InlineKeyboardButton("❓", callback_data=f"casilla_{pos}"))
        botones.append(fila)
    return InlineKeyboardMarkup(botones)

# ------------------ COMANDOS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    crear_usuario(user_id)

    keyboard = [
        [InlineKeyboardButton("🎮 Jugar", callback_data="jugar")],
        [InlineKeyboardButton("📊 Perfil", callback_data="perfil")]
    ]

    await update.message.reply_text(
        "🔥 Bienvenido al bot\nElige una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ------------------ BOTONES ------------------

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    if query.data == "jugar":
        tablero = generar_tablero()
        context.user_data["tablero"] = tablero
        context.user_data["descubiertas"] = []

        await query.message.reply_text(
            "💣 Encuentra los diamantes",
            reply_markup=teclado_tablero()
        )

    elif query.data.startswith("casilla_"):
        pos = int(query.data.split("_")[1])
        tablero = context.user_data.get("tablero")
        descubiertas = context.user_data.get("descubiertas")

        if pos in descubiertas:
            return

        descubiertas.append(pos)

        if tablero[pos] == "💣":
            usuarios[user_id]["saldo"] -= 10
            usuarios[user_id]["perdidas"] += 1
            guardar_db(usuarios)

            await query.message.edit_text("💥 PERDISTE\nPisaste una mina")
        else:
            usuarios[user_id]["saldo"] += 5
            usuarios[user_id]["ganadas"] += 1
            guardar_db(usuarios)

            await query.message.reply_text("💎 ¡Ganaste!")

    elif query.data == "perfil":
        data = usuarios[user_id]
        texto = f"""
📊 PERFIL

💰 Saldo: {data['saldo']}
✅ Ganadas: {data['ganadas']}
❌ Perdidas: {data['perdidas']}
"""
        await query.message.reply_text(texto)

# ------------------ MAIN ------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(botones))

print("Bot corriendo...")
app.run_polling()
