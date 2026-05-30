import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

from collections.abc import Sequence
from pathlib import Path

import players as pl

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:                # existing player
        player = pl.players[update.effective_user.id]
    except KeyError:    # new player
        player = pl.Player(user = update.effective_user)
        pl.players[update.effective_user.id] = player
        
    msg = f"""
Heyo! You can submit:
{player.remaining_slides} more slides,
{player.remaining_titles} more titles, and
{player.remaining_subtitles} more subtitles.
    """
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text=msg
    )

async def save_slide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    
    attachment = update.message.effective_attachment
    await player.save_slide(attachment)
    # file_name = f"{player.count_slides + 1}"
    # file_path = player.path / Path(file_name)
    # file = await attachment.get_file()
    # await file.download_to_drive(file_path)
    # player.update_slides()
    
    msg = f"""
    Awesome! You can submit {player.remaining_slides} more slides.
    """
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text=msg
    )

if __name__ == '__main__':
    pl.load_players()
    
    with open("token.env") as f:
        TOKEN = f.read()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(
        filters.ANIMATION
        | filters.PHOTO
        | filters.Document.IMAGE
        | filters.Document.GIF
        | filters.Document.JPG,
        save_slide
    ))
    
    app.add_handler(CommandHandler("start", start))
    
    app.run_polling()