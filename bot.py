import logging
from telegram import Update
from telegram.ext import (
    filters, ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, ConversationHandler
)

from collections.abc import Sequence
from pathlib import Path

import players as pl

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:                # existing player
        player = pl.players[update.effective_user.id]
    except KeyError:    # new player
        player = pl.Player(user = update.effective_user)
        pl.players[update.effective_user.id] = player
        
    await update.message.reply_text(f"""
Heyo {player.first_name}! You can submit:
{player.remaining_slides} more slides,
{player.remaining_titles} more titles, and
{player.remaining_subtitles} more subtitles.

Don't know what you're doing? Ask for /help.
    """)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Here's what you can do:
/start - Check how many slides, titles, and subtitles you submitted
/help - See this list
/rules - See the rules of the PPTX LOLZ(TM) game
/examples - See some ideas for submissions

/title - Submit a presentation title in the following message
/subtitle - Submit a subtitle in the following message
To submit a slide, just send it!
PPTX LOLZ(TM) supports images, animated GIFs, and uncompressed documents (PNGs, GIFs, JPGs)

/clear_slides - Delete ALL sildes
/clear_titles - Delete ALL titles
/clear_subtitles - Delete ALL subtitles
    """)
    
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Here's how PPTX LOLZ(patent pending) v2.0.9a (i lost the source code i had from 2 years ago) works:

Each player must give a presentation, but nobody knows their topic nor slides in advance. Everyone must improvise on the fly and maintain composure.
The slides, titles and subtitles are submitted by other players in advance and kept in secrecy - only the PPTX LOLZ (patent pending) bot knows who sent what.

When the meeting begins, the presentation are generated on the fly for each player: all contents are randomly selected from OTHER PLAYERS' submissions.
Each player is guaranteed to see one slide from each adversary. This means that the total playtime grows quadratically with the number of players!
As such, it is adviced to limit the presentations to ONE MINUTE PER SLIDE for each player. Anyone who goes overtime shall get shamed.

Sounds stressful? Good - your presentations will be graded and are worth 0.5 ECTS. Enjoy!

(Did I miss anything? Hit me up and let me know.)
    """)
    
async def examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Here's some example submissions to help you get the ideas flowing:

Slides: NO NSFW OR EXPLICIT CONTENT. We will be playing this in a shared space.
- Gaussian Gauss
- Furry lesbians making out (as long as it's SFW it's allowed)
- Complex circuit diagrams
- Vomit-inducing nonsensical AI-generated circuit diagrams
- Your favorite meme
- Quote Of The Day

Titles:
- Why You Should Skip Breakfast
- the situation is getting out of control
- My childhood pictures :)
- A Very Scientific Title With Several Acronyms

Subtitles:
- co-authored with Univ. Prof. Dipl.-Ing. [Name Surname]
- (presented in silly puppy voice)
- (Try Not To Laugh (Impossible))
- We did the Science. The numbers don't lie.
The subtitles should aid the titles, but NOT contain the actual topics to avoid semantic conflict.

Remember, you want to submit something that OTHER PLAYERS will present in front of you. Choose your strategy accordingly.
    """)
    


async def save_slide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    
    if player.remaining_slides > 0:
        attachment = update.message.effective_attachment
        if isinstance(attachment, Sequence):    # Photos are weird :/
            attachment = attachment[-1]
            await player.save_slide(attachment, "jpg")
        else:
            await player.save_slide(attachment)
        
        await update.message.reply_text(f"""
Saved! You can submit {player.remaining_slides} more slides.
        """)
    else:
        await update.message.reply_text("""
You're out of slides!
You can delete ALL of them and start fresh with /clear_slides.
        """)
    
async def save_gif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    
    if player.remaining_slides > 0:
        attachment = update.message.effective_attachment
        await update.message.reply_text(f"""
Converting the GIF, please wait...
        """)
        await player.save_gif(attachment)
        
        await update.message.reply_text(f"""
Saved! You can submit {player.remaining_slides} more slides.
        """)
    else:
        await update.message.reply_text("""
You're out of slides!
You can delete ALL of them and start fresh with /clear_slides.
        """)


    
async def input_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    if player.remaining_titles > 0:
        await update.message.reply_text("""
Enter one title:
(or type /cancel if you changed your mind)
        """)
        return INPUT_TITLE
    else:
        await update.message.reply_text("""
You're out of titles!
You can delete ALL of them and start fresh with /clear_titles.
        """)
        return

async def save_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    player.save_title(update.message.text)
    
    await update.message.reply_text(
        f"Saved! You can submit {player.remaining_titles} more titles."
    )
    return ConversationHandler.END



async def input_subtitle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    if player.remaining_subtitles > 0:
        await update.message.reply_text("""
Enter one subtitle:
(or type /cancel if you changed your mind)
        """)
        return INPUT_SUBTITLE
    else:
        await update.message.reply_text("""
You're out of subtitles!
You can delete ALL of them and start fresh with /clear_subtitles.
        """)
        return

async def save_subtitle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    player.save_subtitle(update.message.text)
    
    await update.message.reply_text(
        f"Saved! You can submit {player.remaining_subtitles} more subtitles."
    )
    return ConversationHandler.END



async def cancel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No problem.")
    return ConversationHandler.END



async def clear_slides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    player.clear_slides()
    await update.message.reply_text(
        f"All slides cleared! You can submit {player.remaining_slides} more slides."
    )
    
async def clear_titles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    player.clear_titles()
    await update.message.reply_text(
        f"All titles cleared! You can submit {player.remaining_titles} more titles."
    )
    
async def clear_subtitles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = pl.players[update.effective_user.id]
    player.clear_subtitles()
    await update.message.reply_text(
        f"All subtitles cleared! You can submit {player.remaining_subtitles} more subtitles."
    )



INPUT_TITLE, INPUT_SUBTITLE = range(2)

if __name__ == '__main__':
    pl.load_players()
    
    with open("token.env") as f:
        TOKEN = f.read()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("examples", examples))
    app.add_handler(CommandHandler("clear_slides", clear_slides))
    app.add_handler(CommandHandler("clear_titles", clear_titles))
    app.add_handler(CommandHandler("clear_subtitles", clear_subtitles))

    app.add_handler(MessageHandler(
        filters.PHOTO
        | filters.Document.IMAGE
        | filters.Document.GIF
        | filters.Document.JPG,
        save_slide
    ))
    app.add_handler(MessageHandler(
        filters.ANIMATION,
        save_gif
    ))
    
    app.add_handler(ConversationHandler(
        entry_points = [
            CommandHandler("title", input_title),
            CommandHandler("subtitle", input_subtitle),
        ],
        states = {
            INPUT_TITLE:
                [MessageHandler(filters.TEXT & ~filters.COMMAND, save_title)],
            INPUT_SUBTITLE:
                [MessageHandler(filters.TEXT & ~filters.COMMAND, save_subtitle)],
        },
        fallbacks = [CommandHandler("cancel", cancel_input)]
    ))
    
    app.run_polling()