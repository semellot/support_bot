import argparse
import json
import os

from dotenv import load_dotenv

from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={'parent': parent, 'intent': intent}
    )

    print('Intent created: {}'.format(response))


if __name__ == '__main__':
    load_dotenv()
    google_project_id = os.getenv('GOOGLE_PROJECT_ID')

    parser = argparse.ArgumentParser()
    parser.add_argument('--json', help='Название файла json', default='questions.json')
    args = parser.parse_args()

    with open(args.json, 'r') as json_file:
        questions_json = json_file.read()
    questions = json.loads(questions_json)

    for intent, question in questions.items():
        create_intent(
            google_project_id,
            intent,
            question['questions'],
            [question['answer']],
        )
