import os
import time
import aiohttp
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# ─────────────────────────────────────────
# 🚀 START
# ─────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("📋 Menu", callback_data="menu"),
         InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("📡 Ping", callback_data="ping"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ]
    await update.message.reply_text(
        f"👋 Welcome, *{user.first_name}*!\n\n"
        f"🤖 I'm *Bishop\\_bot* — your all-in-one Telegram assistant.\n\n"
        f"Use the buttons below to get started 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─────────────────────────────────────────
# 📡 PING
# ─────────────────────────────────────────

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("📡 Pinging...")
    end_time = time.time()
    ms = round((end_time - start_time) * 1000)
    await msg.edit_text(f"✅ *Pong!*\n⚡ Response time: `{ms}ms`", parse_mode="Markdown")

# ─────────────────────────────────────────
# 🔤 PREFIX
# ─────────────────────────────────────────

async def prefix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔤 *Prefix Settings*\n\n"
        "Current prefix: `/`\n\n"
        "All commands start with `/`\n"
        "Example: `/ping`, `/anime Naruto`",
        parse_mode="Markdown"
    )

# ─────────────────────────────────────────
# 👤 USER TOOLS
# ─────────────────────────────────────────

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"🆔 Your Telegram ID: `{user.id}`",
        parse_mode="Markdown"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"👤 *Your Info:*\n"
        f"Name: {user.full_name}\n"
        f"Username: @{user.username or 'None'}\n"
        f"ID: `{user.id}`\n"
        f"Language: {user.language_code or 'Unknown'}",
        parse_mode="Markdown"
    )

# ─────────────────────────────────────────
# 🤖 AI MODULE (Groq)
# ─────────────────────────────────────────

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage: /ai <your message>\nExample: /ai What is anime?"
        )
        return
    user_message = " ".join(context.args)
    msg = await update.message.reply_text("🤖 Thinking...")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        await msg.edit_text("❌ AI service not configured.")
        return
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": user_message}],
                "max_tokens": 500
            }
        ) as resp:
            data = await resp.json()
            reply = data["choices"][0]["message"]["content"]
            await msg.edit_text(f"🤖 *AI:*\n{reply}", parse_mode="Markdown")

# ─────────────────────────────────────────
# 🎌 ANIME MODULE
# ─────────────────────────────────────────

async def anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /anime <name>\nExample: /anime Naruto")
        return
    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching for *{query}*...", parse_mode="Markdown")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.jikan.moe/v4/anime?q={query}&limit=1") as resp:
            data = await resp.json()
            if not data["data"]:
                await update.message.reply_text("❌ Anime not found!")
                return
            a = data["data"][0]
            text = (
                f"🎌 *{a['title']}*\n"
                f"⭐ Score: {a.get('score', 'N/A')}\n"
                f"📺 Episodes: {a.get('episodes', 'N/A')}\n"
                f"📅 Status: {a.get('status', 'N/A')}\n"
                f"🎭 Genres: {', '.join(g['name'] for g in a.get('genres', []))}\n\n"
                f"📝 {a.get('synopsis', 'No description')[:300]}..."
            )
            await update.message.reply_text(text, parse_mode="Markdown")

async def top_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Fetching top anime...")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.jikan.moe/v4/top/anime?limit=10") as resp:
            data = await resp.json()
            text = "🏆 *Top 10 Anime:*\n\n"
            for i, a in enumerate(data["data"], 1):
                text += f"{i}. {a['title']} ⭐{a.get('score', 'N/A')}\n"
            await update.message.reply_text(text, parse_mode="Markdown")

async def waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 Fetching anime image...")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.waifu.pics/sfw/waifu") as resp:
            data = await resp.json()
            image_url = data["url"]
            await update.message.reply_photo(
                photo=image_url,
                caption="🌸 Here's your anime image!\nUse /waifu again for another one."
            )

# ─────────────────────────────────────────
# 👮 ADMIN MODULE
# ─────────────────────────────────────────

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You need to be an admin to use this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to ban them.")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.message.chat_id, user.id)
    await update.message.reply_text(f"🚫 {user.full_name} has been banned!")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You need to be an admin to use this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to kick them.")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.message.chat_id, user.id)
    await context.bot.unban_chat_member(update.message.chat_id, user.id)
    await update.message.reply_text(f"👢 {user.full_name} has been kicked!")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You need to be an admin to use this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to warn them.")
        return
    user = update.message.reply_to_message.from_user
    await update.message.reply_text(f"⚠️ {user.full_name} has been warned! Please follow the rules.")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You need to be an admin to use this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to mute them.")
        return
    user = update.message.reply_to_message.from_user
    await context.bot.restrict_chat_member(
        update.message.chat_id, user.id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text(f"🔇 {user.full_name} has been muted!")

# ─────────────────────────────────────────
# 🔘 BUTTON HANDLER
# ─────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    back_button = [[InlineKeyboardButton("🔙 Back", callback_data="start")]]

    if data == "start":
        keyboard = [
            [InlineKeyboardButton("📋 Menu", callback_data="menu"),
             InlineKeyboardButton("❓ Help", callback_data="help")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
             InlineKeyboardButton("👑 Premium", callback_data="premium")],
            [InlineKeyboardButton("📡 Ping", callback_data="ping"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")],
        ]
        await query.edit_message_text(
            "👋 Welcome back!\n\n🤖 I'm *Bishop\\_bot* — your all-in-one assistant.\n\nUse the buttons below 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu":
        keyboard = [
            [InlineKeyboardButton("👤 User Tools", callback_data="cat_user"),
             InlineKeyboardButton("🎌 Anime", callback_data="cat_anime")],
            [InlineKeyboardButton("🤖 AI Chat", callback_data="cat_ai"),
             InlineKeyboardButton("👑 Premium", callback_data="premium")],
            [InlineKeyboardButton("👮 Admin Tools", callback_data="cat_admin")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")],
        ]
        await query.edit_message_text(
            "📋 *Main Menu*\n\nChoose a category below 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "help":
        keyboard = [
            [InlineKeyboardButton("👤 User Tools", callback_data="cat_user"),
             InlineKeyboardButton("🎌 Anime", callback_data="cat_anime")],
            [InlineKeyboardButton("🤖 AI Chat", callback_data="cat_ai"),
             InlineKeyboardButton("👮 Admin Tools", callback_data="cat_admin")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")],
        ]
        await query.edit_message_text(
            "❓ *Help Center*\n\nSelect a category to see commands 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "cat_user":
        await query.edit_message_text(
            "👤 *User Tools*\n\n"
            "/id — Your Telegram UID\n"
            "/info — Your profile info\n"
            "/ping — Bot response time\n"
            "/prefix — Command prefix info",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_button)
        )

    elif data == "cat_anime":
        await query.edit_message_text(
            "🎌 *Anime Commands*\n\n"
            "/anime <name> — Search anime\n"
            "/top — Top 10 anime list\n"
            "/waifu — Random anime image",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_button)
        )

    elif data == "cat_ai":
        await query.edit_message_text(
            "🤖 *AI Chat*\n\n"
            "/ai <message> — Chat with AI\n\n"
            "Example: `/ai What is the meaning of life?`\n\n"
            "Powered by Groq x Llama 3 ⚡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_button)
        )

    elif data == "cat_admin":
        await query.edit_message_text(
            "👮 *Admin Tools*\n\n"
            "/ban — Ban a user\n"
            "/kick — Kick a user\n"
            "/warn — Warn a user\n"
            "/mute — Mute a user\n\n"
            "⚠️ Reply to a user's message to use these commands.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_button)
        )

    elif data == "settings":
        keyboard = [
            [InlineKeyboardButton("🔔 Notifications: ON", callback_data="notif_toggle")],
            [InlineKeyboardButton("🌐 Language: English", callback_data="lang_toggle")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")],
        ]
        await query.edit_message_text(
            "⚙️ *Settings*\n\nCustomize your experience 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "notif_toggle":
        await query.answer("🔔 Notifications feature coming soon!", show_alert=True)

    elif data == "lang_toggle":
        await query.answer("🌐 Language settings coming soon!", show_alert=True)

    elif data == "premium":
        keyboard = [
            [InlineKeyboardButton("💎 Get Premium", callback_data="get_premium")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")],
        ]
        await query.edit_message_text(
            "👑 *Premium Features*\n\n"
            "✅ Unlimited AI Chat\n"
            "✅ Free Fire Stats\n"
            "✅ TikTok Downloader\n"
            "✅ AI Image Generator\n"
            "✅ Priority Support\n\n"
            "🚀 *Coming Soon!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "get_premium":
        await query.answer("👑 Premium coming soon! Stay tuned.", show_alert=True)

    elif data == "ping":
        await query.edit_message_text(
            "✅ *Pong!*\n⚡ Bot is online and responding!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_button)
        )

    elif data == "about":
        keyboard = [
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Bishop_fxx")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")],
        ]
        await query.edit_message_text(
            "ℹ️ *About Bishop\\_bot*\n\n"
            "🤖 Version: 1.0.0\n"
            "👨‍💻 Developer: @Bishop_fxx\n"
            "📅 Created: 2026\n\n"
            "Bishop\\_bot is a powerful all-in-one Telegram bot "
            "with anime search, admin tools, AI chat and more!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ─────────────────────────────────────────
# 🚀 MAIN
# ─────────────────────────────────────────

app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", start))
app.add_handler(CommandHandler("menu", start))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("prefix", prefix))
app.add_handler(CommandHandler("id", myid))
app.add_handler(CommandHandler("myuid", myid))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("ai", ai_chat))
app.add_handler(CommandHandler("anime", anime))
app.add_handler(CommandHandler("top", top_anime))
app.add_handler(CommandHandler("waifu", waifu))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("kick", kick))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
