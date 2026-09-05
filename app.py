import os
import threading

from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ==================================================
# FLASK WEBSITE
# ==================================================

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SkillSwap</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 30px 20px;
                background: #f5f7fb;
                text-align: center;
            }

            .container {
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 30px 20px;
                border-radius: 20px;
            }

            h1 {
                font-size: 32px;
            }

            p {
                color: #555;
            }

            button {
                width: 100%;
                padding: 15px;
                margin-top: 10px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h1>🤝 SkillSwap</h1>
            <p>Learn a skill. Teach a skill. Swap knowledge.</p>

            <button>🎓 I Want to Learn</button>
            <button>👨‍🏫 I Want to Teach</button>
        </div>
    </body>
    </html>
    """


# ==================================================
# TELEGRAM BOT
# ==================================================

NAME, ROLE, SKILL = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to SkillSwap!\n\n"
        "Let's create your profile.\n\n"
        "What is your name?"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        f"Nice to meet you, {update.message.text}! 👋\n\n"
        "Do you want to:\n\n"
        "1️⃣ Learn a skill\n"
        "2️⃣ Teach a skill\n\n"
        "Reply with Learn or Teach."
    )

    return ROLE


async def get_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text.lower()

    if role not in ["learn", "teach"]:
        await update.message.reply_text(
            "Please reply with either Learn or Teach."
        )
        return ROLE

    context.user_data["role"] = role

    await update.message.reply_text(
        "Great! 💡\n\n"
        "What skill are you interested in?"
    )

    return SKILL


async def get_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["skill"] = update.message.text

    name = context.user_data["name"]
    role = context.user_data["role"]
    skill = context.user_data["skill"]

    await update.message.reply_text(
        "✅ Profile created!\n\n"
        f"👤 Name: {name}\n"
        f"🎯 Goal: {role.title()}\n"
        f"💡 Skill: {skill}\n\n"
        "Welcome to SkillSwap! 🚀"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration cancelled.")
    return ConversationHandler.END


def run_telegram_bot():
    bot_token = os.environ.get("BOT_TOKEN")

    if not bot_token:
        print("ERROR: BOT_TOKEN is not configured.")
        return

    telegram_app = Application.builder().token(bot_token).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],
            ROLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_role
                )
            ],
            SKILL: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_skill
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )

    telegram_app.add_handler(conversation)

    print("🤖 SkillSwap Telegram bot is running!")

    telegram_app.run_polling()


# ==================================================
# START TELEGRAM IN BACKGROUND
# ==================================================

bot_thread = threading.Thread(
    target=run_telegram_bot,
    daemon=True
)

bot_thread.start()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
