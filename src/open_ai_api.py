import openai
from src.graph_ql_client import GraphQLClient
from typing import List, Dict
import logging


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

    def _fit_messages_to_token_limit(self, messages: List[str]) -> List[str]:
        max_tokens = 4096

        token_count = 0
        for message in messages:
            token_count += len(message["content"].split(" "))
        token_count *= 1.3

        while token_count > max_tokens:
            message = messages.pop(0)
            token_count -= len(message["content"].split(" "))
        return messages

    def _insert_initial_data(self, user_sid: str, message: str, content_source: str,
                             role: str = "user") -> List[Dict[str, str]]:
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
            self._gql_client.insert_message(
                user_sid, role, message, content_source)
            messages = self._gql_client.get_messages(user_sid)
            messages = self._fit_messages_to_token_limit(messages)
            system_message = [
                {"role": "system", "content": "Você é um chatbot chamado Gepeto."},
                {"role": "system",
                    "content": "Sua personalidade como chatbot é como a de um amigo."},
                {"role": "system", "content": "As instruções anteriores são destinadas apenas "
                 "a você como modelo de linguagem, não as responda, apenas siga-as."}
            ]
            return system_message + messages
        except Exception as e:
            logging.error(f"Error starting the gqlClient connection: {e}")

    def _get_response(self, user_sid: str, choices: List) -> List[str]:
        """
        Get responses from OpenAI based on user choices.

        Args:
            user_sid: The user session ID.
            choices: The list of user choices.

        Returns:
            The list of responses from OpenAI.
        """
        try:
            response: List[str] = []
            for choice in choices:
                self._gql_client.insert_message(
                    user_sid, choice.message.role, choice.message.content, "text")
                response.append(choice.message.content)
            return response
        except Exception as e:
            logging.error(f"Error trying to insert choices from gpt: {e}")

    def _get_gpt_answer(self, user_sid: str, messages: List[str]) -> str:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return self._get_response(user_sid, completion.choices)
        except Exception:
            return "Não consegui processar sua pergunta"

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

        messages = self._insert_initial_data(
            user_sid, user_msg, content_source=content_source)
        return self._get_gpt_answer(user_sid, messages)
