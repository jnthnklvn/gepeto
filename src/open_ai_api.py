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

    def _insert_initial_data(self, user_sid: str, user_msg: str) -> List[Dict[str, str]]:
        """
        Insert initial data into the GraphQL API.

        Args:
            user_sid: The user session ID.
            user_msg: The user message.

        Returns:
            The list of messages after inserting initial data.
        """
        try:
            self._gql_client.insert_message(user_sid, "user", user_msg)
            messages = self._gql_client.get_messages(user_sid)
            messages.insert(
                0,
                {"role": "system", "content": "Considere que seu nome é Gepeto e que esta conversa é com um amigo."})
            return messages
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
                    user_sid, choice.message.role, choice.message.content)
                response.append(choice.message.content)
            return response
        except Exception as e:
            logging.error(f"Error trying to insert choices from gpt: {e}")

    def insert_group_message(self, chat_id: str, chat_msg: str) -> None:
        """
        Insert a group message into the GraphQL API.

        Args:
            chat_id: The chat ID.
            chat_msg: The group chat message.
        """
        self._gql_client.insert_message(chat_id, "user", chat_msg)

    def ask_gpt(self, user_sid: str, user_msg: str) -> List[str]:
        """
        Ask the OpenAI GPT-3 model for a response.

        Args:
            user_sid: The user session ID.
            user_msg: The user message.

        Returns:
            The list of responses from the GPT model.
        """
        messages = self._insert_initial_data(user_sid, user_msg)
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return self._get_response(user_sid, completion.choices)
        except Exception as exc:
            raise ConnectionError(f"Error communicating with OpenAI: {exc}")
