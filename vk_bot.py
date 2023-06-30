import logging
import os
import random
import requests

from dotenv import load_dotenv

from google.cloud import api_keys_v2
from google.cloud.api_keys_v2 import Key
from google.cloud import dialogflow

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType


logger = logging.getLogger('Logger for vk_bot')

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

        if response.query_result.intent.is_fallback:
            return False
        else:
            return response.query_result.fulfillment_text


def echo(event, vk_api, google_project_id):
    answer = detect_intent_texts(google_project_id, event.user_id, [event.text], 'ru-RU')
    if answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message=answer,
            random_id=random.randint(1,1000)
        )

def main() -> None:
    load_dotenv()
    vk_group_token = os.getenv('VK_GROUP_TOKEN')
    google_project_id = os.getenv('GOOGLE_PROJECT_ID')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api, google_project_id)
    except requests.exceptions.HTTPError as err:
        logger.warning(f'Ошибка!\n{err}')


if __name__ == '__main__':
    main()
