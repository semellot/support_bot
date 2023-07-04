import logging
import os
import random
import requests

from telegram_logger import TelegramLogsHandler
from dialogflow_api import detect_intent_texts

from dotenv import load_dotenv

from google.cloud import api_keys_v2
from google.cloud.api_keys_v2 import Key
from google.cloud import dialogflow

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType


logger = logging.getLogger('Logger for vk_bot')


def send_answer(event, vk_api, google_project_id):
    answer = detect_intent_texts(google_project_id, event.user_id, event.text, 'ru-RU')
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
                send_answer(event, vk_api, google_project_id)
    except requests.exceptions.HTTPError as err:
        logger.warning(f'Ошибка!\n{err}')


if __name__ == '__main__':
    main()
