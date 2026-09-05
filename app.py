import os
import threading

from flask import Flask, render_template, request

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
# SKILLSWAP WEBSITE
# ==================================================

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        skill = request.form.get("skill")

        print("================================")
        print("NEW SKILLSWAP USER")
        print("Name:", name)
        print("Email:", email)
        print("Skill:", skill)
        print("================================")

        return f"""
        <html>
        <head>
            <title>SkillSwap - Welcome</title>
        </head>

        <body>
            <h1>Welcome to SkillSwap, {name}! 🎉</h1>

            <p>Your signup was successful.</p>

            <p><strong>Email:</strong> {email}</p>
            <p><strong>Skill:</strong> {skill}</p>

            <br>

            <a href="/">Go back to SkillSwap</a>
        </body>
        </html>
        """

    return render_template("signup.html")


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

    await update.message.reply_text(
        "Registration cancelled."
    )

    return ConversationHandler.END


# ==================================================
# RUN TELEGRAM BOT
# ==================================================

def run_telegram_bot():

    bot_token = os.environ.get("BOT_TOKEN")

    if not bot_token:

        print("ERROR: BOT_TOKEN is not configured.")

        return

    telegram_app = (
        Application
        .builder()
        .token(bot_token)
        .build()
    )

    conversation = ConversationHandler(

        entry_points=[
            CommandHandler("start", start)
        ],

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
# START TELEGRAM BOT IN BACKGROUND
# ==================================================

bot_thread = threading.Thread(
    target=run_telegram_bot,
    daemon=True
)

bot_thread.start()


# ==================================================
# START FLASK SERVER
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get("PORT", 5000)
        )
    )
