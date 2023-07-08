import logging
import os
import requests

from telegram_logger import TelegramLogsHandler
from dialogflow_api import detect_intent_texts

from dotenv import load_dotenv

from google.cloud import api_keys_v2
from google.cloud.api_keys_v2 import Key
from google.cloud import dialogflow

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


logger = logging.getLogger('Logger for tg_bot')


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def send_answer(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    google_project_id = os.environ['GOOGLE_PROJECT_ID']
    has_answer, answer = detect_intent_texts(google_project_id, user.id, update.message.text, 'ru-RU')
    update.message.reply_text(answer)


def main() -> None:
    load_dotenv()
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    os.environ['GOOGLE_PROJECT_ID'] = os.getenv('GOOGLE_PROJECT_ID')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_answer))

    try:
        updater.start_polling()
        updater.idle()
    except requests.exceptions.HTTPError as err:
        logger.warning(f'Ошибка!\n{err}')


if __name__ == '__main__':
    main()
