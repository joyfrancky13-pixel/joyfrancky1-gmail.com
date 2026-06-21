from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8941502684:AAGGo0w1njEw0VDEgtKiBWBIDTnHRKTiiqM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot foot en ligne ⚽ Envoie /score pour tester")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Barça 2-0 Real - Buts: Lewandowski 15'")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("score", score))
app.run_polling()
