import os
from re import L
import openai
import config


openai.api_key = os.environ["OPENAI_API_KEY"]


def chat(messages) -> str:
    from pprint import pprint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0]["message"]["content"].strip()


def main():
    messages = []
    while True:
        user_input = input('質問: ')
        if user_input == 'end':
            break
        else:
            messages += [{'role': 'user', "content": user_input,}]
            response = chat(messages)
            messages += [{'role': 'assistant', "content": response}]


if __name__ == "__main__":
    main()