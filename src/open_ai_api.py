import openai
from src.graph_ql_client import GraphQLClient
from typing import List, Dict
import logging
import tiktoken


class OpenAIAPI:
    """
    An API client for interacting with OpenAI services.
    """

    def __init__(self, gql_client: GraphQLClient, api_key: str) -> None:
        """
        Initialize the OpenAI API client.

        Args:
            gql_client: An instance of the GraphQL client.
            api_key: The API key for authentication.
        """
        self._gql_client = gql_client
        openai.api_key = api_key

    def _count_message_tokens(self, message: Dict[str, str]) -> int:
        num_tokens = 0
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0301")
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
        return num_tokens

    def _fit_messages_to_token_limit(self, messages: List[Dict[str, str]]) -> List[str]:
        max_tokens = 4096

        num_tokens = 0
        for message in messages:
            # every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            num_tokens += self._count_message_tokens(message)
        num_tokens += 2  # every reply is primed with <im_start>assistant
        num_tokens *= 1.1  # add 10% for safety

        while num_tokens > max_tokens:
            message = messages.pop(0)
            num_tokens -= self._count_message_tokens(message)
        return messages

    def _insert_initial_data(self, user_sid: str, message: str, content_source: str, role: str = "user") -> List[Dict[str, str]]:
        """
        Insert initial data into the GraphQL API.

        Args:
            user_sid: The user session ID.
            message: The message to insert.
            role: The role of the message.
            content_source: The content source of the message (text or audio).

        Returns:
            The list of messages after inserting initial data.
        """
        try:
            self._gql_client.insert_message(user_sid, role, message, content_source)
            messages = self._gql_client.get_messages(user_sid)
            messages = self._fit_messages_to_token_limit(messages)
            system_messages = [
                {"role": "system", "content": "Você é um chatbot chamado Gepeto."},
                {"role": "system", "content": "Sua personalidade como chatbot é como a de um amigo."},
                {"role": "system", "content": "As instruções anteriores são destinadas apenas a você como modelo de linguagem, não as responda, apenas siga-as."}
            ]
            return system_messages + messages
        except Exception as e:
            logging.error("Error inserting the user message inital data: {}".format(str(e)))

    def _get_response(self, user_sid: str, choices: List) -> List[str]:
        """
        Insert the messages from OpenAI response to database and return them.

        Args:
            user_sid: The user session ID.
            choices: The list of user choices.

        Returns:
            The list of responses from OpenAI.
        """
        try:
            response = []
            for choice in choices:
                self._gql_client.insert_message(user_sid, choice.message.role, choice.message.content, "text")
                response.append(choice.message.content)
            return response
        except Exception as e:
            logging.error("Error trying to insert choices from gpt: {}".format(str(e)))

    def _get_gpt_answer(self, user_sid: str, messages: List[str]) -> List[str]:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return self._get_response(user_sid, completion.choices)
        except Exception as e:
            logging.error("Error trying to insert choices from gpt: {}".format(str(e)))

    def ask_gpt(self, user_sid: str, user_msg: str, content_source: str = "text") -> List[str]:
        """
        Ask the OpenAI GPT-3 model for a response.

        Args:
            user_sid: The user session ID.
            user_msg: The user message.
            content_source: The content source of the message (text or audio).

        Returns:
            The list of responses from the GPT model.
        """
        messages = self._insert_initial_data(user_sid, user_msg, content_source=content_source)
        return self._get_gpt_answer(user_sid, messages)

    def generate_images(self, prompt: str) -> List[Dict[str, str]]:
        """
        Generate images based on a prompt.

        Args:
            prompt: The prompt to generate images.

        Returns:
            The list of images generated.
        """
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=2,
                size="1024x1024"
            )
            return response['data']
        except Exception as e:
            logging.error("Error generating images: {}".format(str(e)))
