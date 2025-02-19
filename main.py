from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Please send me the URL you want to open in the WebApp.')

async def set_url(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.title.string if soup.title else 'No title available'
    description = soup.find('meta', attrs={'name': 'description'})
    description = description['content'] if description else 'No description available'
    
    # Extract favicon
    icon_link = soup.find('link', rel='icon')
    icon_url = icon_link['href'] if icon_link else None
    
    # Extract preview image or video
    preview_image = soup.find('meta', property='og:image')
    preview_image_url = preview_image['content'] if preview_image else None
    
    keyboard = [
        [InlineKeyboardButton(f"Open {title}", web_app=WebAppInfo(url=url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f'*{title}*\n{description}'
    if icon_url:
        message_text += f'\nIcon: {icon_url}'
    if preview_image_url:
        message_text += f'\nPreview: {preview_image_url}'
    
    await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode='MarkdownV2')

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_url))
    application.run_polling()

if __name__ == '__main__':
    main()