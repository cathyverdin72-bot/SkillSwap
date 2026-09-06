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

    # Show signup page
    if request.method == "GET":
        return render_template("signup.html")


    # --------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------

    name = request.form.get("name", "").strip()

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "")

    skill_teach = request.form.get(
        "skill_teach",
        ""
    ).strip()

    skill_learn = request.form.get(
        "skill_learn",
        ""
    ).strip()

    goal = request.form.get(
        "goal",
        ""
    ).strip().lower()


    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if not name:
        return "Please enter your name.", 400

    if not email:
        return "Please enter your email.", 400

    if not password:
        return "Please create a password.", 400

    if not skill_teach:
        return "Please enter a skill you can teach.", 400

    if not skill_learn:
        return "Please enter a skill you want to learn.", 400

    if goal not in ["learn", "teach", "both"]:
        return "Please choose your SkillSwap journey.", 400


    # --------------------------------------------------
    # CHECK DATABASE
    # --------------------------------------------------

    if supabase is None:

        return """
        <h2>Database connection is not configured.</h2>
        <p>Please check your Supabase environment variables.</p>
        """, 500


    # --------------------------------------------------
    # STARTING SKILLS PROFILE
    # --------------------------------------------------

    starting_points = 0

    starting_level = "Beginner"


    # --------------------------------------------------
    # PASSWORD HASH
    # --------------------------------------------------

    password_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


    # --------------------------------------------------
    # CREATE USER
    # --------------------------------------------------

    try:

        response = supabase.table(
            "users"
        ).insert({

            "name": name,

            "email": email,

            "password_hash": password_hash,

            "skill": skill_teach,

            "skill_points": starting_points,

            "level": starting_level,

            "skill_to_teach": skill_teach,

            "skill_to_learn": skill_learn,

            "goal": goal

        }).execute()


        # --------------------------------------------------
        # SUCCESS PAGE
        # --------------------------------------------------

        return f"""
        <!DOCTYPE html>

        <html lang="en">

        <head>

            <meta charset="UTF-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <title>Welcome to SkillSwap</title>

            <style>

                * {{
                    box-sizing: border-box;
                }}

                body {{

                    margin: 0;

                    font-family:
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        sans-serif;

                    background:
                        linear-gradient(
                            135deg,
                            #f5f3ff,
                            #ffffff,
                            #eef2ff
                        );

                    min-height: 100vh;

                    display: flex;

                    align-items: center;

                    justify-content: center;

                    padding: 20px;

                    color: #171717;

                }}


                .card {{

                    width: 100%;

                    max-width: 430px;

                    background: white;

                    border-radius: 25px;

                    padding: 32px 24px;

                    text-align: center;

                    box-shadow:
                        0 20px 60px
                        rgba(0,0,0,.08);

                }}


                .emoji {{

                    font-size: 55px;

                    margin-bottom: 10px;

                }}


                h1 {{

                    margin-bottom: 8px;

                    color: #6c4cff;

                }}


                .welcome {{

                    color: #666;

                    line-height: 1.5;

                }}


                .level-box {{

                    margin-top: 22px;

                    padding: 20px;

                    background: #f5f3ff;

                    border-radius: 18px;

                }}


                .level {{

                    font-size: 24px;

                    font-weight: 800;

                }}


                .points {{

                    margin-top: 8px;

                    color: #666;

                }}


                .progress {{

                    height: 9px;

                    background: #ded9ff;

                    border-radius: 20px;

                    margin-top: 15px;

                    overflow: hidden;

                }}


                .progress-inner {{

                    width: 0%;

                    height: 100%;

                    background: #6c4cff;

                }}


                .next {{

                    margin-top: 8px;

                    font-size: 12px;

                    color: #777;

                }}


                .skills {{

                    margin-top: 20px;

                    text-align: left;

                }}


                .skills p {{

                    margin: 8px 0;

                    font-size: 14px;

                }}


                .button {{

                    display: block;

                    margin-top: 25px;

                    padding: 14px;

                    border-radius: 13px;

                    background: #6c4cff;

                    color: white;

                    text-decoration: none;

                    font-weight: 700;

                }}

            </style>

        </head>


        <body>

            <div class="card">

                <div class="emoji">
                    🎉
                </div>

                <h1>
                    Welcome to SkillSwap!
                </h1>

                <p class="welcome">

                    Hi <strong>{name}</strong> 👋

                    <br><br>

                    Your SkillSwap journey starts now.

                </p>


                <div class="level-box">

                    <div class="level">
                        🌱 Beginner
                    </div>

                    <div class="points">

                        <strong>0</strong>
                        Skill Points

                    </div>

                    <div class="progress">

                        <div class="progress-inner"></div>

                    </div>

                    <div class="next">

                        0 / 500 points to ⚡ Active

                    </div>

                </div>


                <div class="skills">

                    <p>
                        🎓 <strong>You can teach:</strong>
                        {skill_teach}
                    </p>

                    <p>
                        📚 <strong>You want to learn:</strong>
                        {skill_learn}
                    </p>

                    <p>
                        🎯 <strong>Your journey:</strong>
                        {goal.title()}
                    </p>

                </div>


                <a
                    class="button"
                    href="/"
                >
                    Continue to SkillSwap →
                </a>

            </div>

        </body>

        </html>
        """


    except Exception as error:

        print(
            "SIGNUP ERROR:",
            error
        )

        return """
        <h2>Unable to create your account.</h2>

        <p>
            The email may already be registered,
            or your database may need the new
            SkillSwap fields.
        </p>

        <a href="/signup">
            Try again
        </a>
        """, 400


# ==================================================
# TELEGRAM BOT
# ==================================================

NAME, ROLE, SKILL = range(3)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "👋 Welcome to SkillSwap!\n\n"

        "Let's create your profile.\n\n"

        "What is your name?"

    )

    return NAME


async def get_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["name"] = (
        update.message.text
    )

    await update.message.reply_text(

        f"Nice to meet you, "
        f"{update.message.text}! 👋\n\n"

        "Do you want to:\n\n"

        "1️⃣ Learn a skill\n"
        "2️⃣ Teach a skill\n\n"

        "Reply with Learn or Teach."

    )

    return ROLE


async def get_role(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    role = update.message.text.lower()


    if role not in [
        "learn",
        "teach"
    ]:

        await update.message.reply_text(

            "Please reply with either "
            "Learn or Teach."

        )

        return ROLE


    context.user_data["role"] = role


    await update.message.reply_text(

        "Great! 💡\n\n"

        "What skill are you interested in?"

    )

    return SKILL


async def get_skill(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["skill"] = (
        update.message.text
    )


    name = context.user_data["name"]

    role = context.user_data["role"]

    skill = context.user_data["skill"]


    await update.message.reply_text(

        "✅ Profile created!\n\n"

        f"👤 Name: {name}\n"

        f"🎯 Goal: {role.title()}\n"

        f"💡 Skill: {skill}\n\n"

        "🌱 Level: Beginner\n"

        "⭐ Skill Points: 0\n\n"

        "Welcome to SkillSwap! 🚀"

    )


    return ConversationHandler.END


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "Registration cancelled."

    )

    return ConversationHandler.END


# ==================================================
# TELEGRAM BOT
# ==================================================

def run_telegram_bot():

    bot_token = os.environ.get(
        "BOT_TOKEN"
    )


    if not bot_token:

        print(
            "ERROR: BOT_TOKEN is not configured."
        )

        return


    telegram_app = (

        Application
        .builder()
        .token(bot_token)
        .build()

    )


    conversation = ConversationHandler(

        entry_points=[

            CommandHandler(
                "start",
                start
            )

        ],

        states={

            NAME: [

                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    get_name
                )

            ],

            ROLE: [

                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    get_role
                )

            ],

            SKILL: [

                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    get_skill
                )

            ],

        },

        fallbacks=[

            CommandHandler(
                "cancel",
                cancel
            )

        ],

    )


    telegram_app.add_handler(
        conversation
    )


    print(
        "🤖 SkillSwap Telegram bot is running!"
    )


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
            os.environ.get(
                "PORT",
                5000
            )
        )

    )
