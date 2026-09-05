import os
import threading
import hashlib

from flask import Flask, render_template, request

from supabase import create_client

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


# ==================================================
# SUPABASE
# ==================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# SIGNUP
# ==================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    skill = request.form.get("skill", "").strip()

    # Check required fields
    if not name or not email or not password or not skill:
        return "Please fill in all fields.", 400

    # Check Supabase connection
    if supabase is None:
        return "Database connection is not configured.", 500

    # Hash password
    password_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    try:

        # Create user
        response = supabase.table("users").insert({
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "skill": skill
        }).execute()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome to SkillSwap</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    background: #f5f3ff;
                    text-align: center;
                    padding: 60px 20px;
                }}

                .card {{
                    background: white;
                    max-width: 420px;
                    margin: auto;
                    padding: 35px 25px;
                    border-radius: 25px;
                    box-shadow: 0 20px 50px rgba(0,0,0,0.08);
                }}

                h1 {{
                    color: #6c4cff;
                }}

                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 13px 22px;
                    background: #6c4cff;
                    color: white;
                    text-decoration: none;
                    border-radius: 12px;
                    font-weight: bold;
                }}

            </style>
        </head>

        <body>

            <div class="card">

                <h1>🎉 Welcome to SkillSwap!</h1>

                <p>
                    Your account has been created successfully.
                </p>

                <p>
                    Hi <strong>{name}</strong> 👋
                </p>

                <p>
                    Your skill: <strong>{skill}</strong>
                </p>

                <a href="/">
                    Continue to SkillSwap
                </a>

            </div>

        </body>
        </html>
        """

    except Exception as error:

        print("SIGNUP ERROR:", error)

        return """
        <h2>Unable to create your account.</h2>
        <p>The email may already be registered.</p>
        <a href="/signup">Try again</a>
        """, 400


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
# TELEGRAM BOT
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
# START TELEGRAM BOT
# ==================================================

bot_thread = threading.Thread(
    target=run_telegram_bot,
    daemon=True
)

bot_thread.start()


# ==================================================
# START FLASK
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get("PORT", 5000)
        )
    )
