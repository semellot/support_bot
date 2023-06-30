import logging
import os

from dotenv import load_dotenv

from google.cloud import api_keys_v2
from google.cloud.api_keys_v2 import Key
from google.cloud import dialogflow

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


logger = logging.getLogger('Logger for tg_bot')

class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = telegram.Bot(token=tg_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(project_id, session_id, texts, language_code):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={'session': session, 'query_input': query_input}
        )

        return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    google_project_id = os.environ['GOOGLE_PROJECT_ID']
    answer = detect_intent_texts(google_project_id, user.id, [update.message.text], 'ru-RU')
    update.message.reply_text(answer)


def main() -> None:
    load_dotenv()
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    os.environ['GOOGLE_PROJECT_ID'] = os.getenv('GOOGLE_PROJECT_ID')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    try:
        updater.start_polling()
        updater.idle()
    except requests.exceptions.HTTPError as err:
        logger.warning(f'Ошибка!\n{err}')


if __name__ == '__main__':
    main()
