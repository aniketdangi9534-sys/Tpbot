import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

conn = sqlite3.connect("bids.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bids (
    chat_id INTEGER PRIMARY KEY,
    bid_value TEXT
)
""")
conn.commit()

async def is_admin(update: Update):
    member = await update.effective_chat.get_member(update.effective_user.id)
    return member.status in ["administrator", "creator"]

async def bid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ Only admin can set bid!")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /bid <amount>")
        return

    bid_value = context.args[0]
    chat_id = update.effective_chat.id

    cursor.execute("REPLACE INTO bids (chat_id, bid_value) VALUES (?, ?)", (chat_id, bid_value))
    conn.commit()

    await update.message.reply_text(f"✅ Bid set to: {bid_value}")

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    cursor.execute("SELECT bid_value FROM bids WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"💰 Current Bid: {result[0]}")
    else:
        await update.message.reply_text("❌ No bid set yet!")

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

app.add_handler(CommandHandler("bid", bid))
app.add_handler(CommandHandler("show", show))

app.run_polling()
