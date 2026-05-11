import os
import aiohttp
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from keep_alive import keep_alive

# ─────────────────────────────────────────
# 🔧 UTILITIES
# ─────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I'm Bishop_bot\n\n"
        "📌 Commands:\n"
        "/help — Show all commands\n"
        "/id — Get your Telegram ID\n"
        "/info — Your profile info\n"
        "/ping — Check if bot is online\n"
        "/anime <name> — Search anime\n"
        "/top — Top 10 anime\n"
        "/ban — Ban a user (admin)\n"
        "/kick — Kick a user (admin)\n"
        "/warn — Warn a user (admin)\n"
        "/mute — Mute a user (admin)\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 *All Commands:*\n\n"
        "👤 *User Tools*\n"
        "/id — Your Telegram UID\n"
        "/info — Your profile info\n"
        "/ping — Bot status\n\n"
        "🎌 *Anime*\n"
        "/anime <name> — Search anime\n"
        "/top — Top 10 anime list\n\n"
        "👮 *Admin Tools*\n"
        "/ban — Ban a user\n"
        "/kick — Kick a user\n"
        "/warn — Warn a user\n"
        "/mute — Mute a user\n\n"
        "⏳ *Coming Soon*\n"
        "Free Fire stats, TikTok downloader, AI image gen",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Bot is online and running!")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(f"🆔 Your Telegram ID: `{user.id}`", parse_mode="Markdown")

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
# 🚀 MAIN
# ─────────────────────────────────────────

app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("id", myid))
app.add_handler(CommandHandler("myuid", myid))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("anime", anime))
app.add_handler(CommandHandler("top", top_anime))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("kick", kick))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("mute", mute))

app.run_polling()
