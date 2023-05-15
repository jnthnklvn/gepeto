import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from typing import List, Dict


class GraphQLClient:
    """
    A client for interacting with a GraphQL API.
    """

    def __init__(self, url: str, api_key: str) -> None:
        """
        Initialize the GraphQL client.

        Args:
            url: The URL of the GraphQL API.
            api_key: The API key for authentication.
        """
        transport = AIOHTTPTransport(url=url, headers={'apiKey': api_key})
        self._client = Client(transport=transport,
                              fetch_schema_from_transport=True)

    def insert_message(self, user_sid: str, role: str, content: str) -> Dict[str, str]:
        """
        Insert a new message into the GraphQL API.

        Args:
            user_sid: The user session ID.
            role: The role of the message.
            content: The content of the message.

        Returns:
            The inserted message.
        """
        insert_query = gql('''
      mutation ($data: MessageInsertInput!) {
        insertOneMessage(data: $data) {
          _id
          user_sid
          role
          content
          created_at
        }
      }
      ''')

        variables = {
            'data': {
                'user_sid': user_sid,
                'role': role,
                'content': content,
                'created_at': datetime.datetime.utcnow().isoformat()
            }
        }

        response = self._client.execute(
            insert_query, variable_values=variables)
        return response['insertOneMessage']

    def get_messages(self, user_sid: str) -> List[Dict[str, str]]:
        """
        Retrieve messages from the GraphQL API for a given user.

        Args:
            user_sid: The user session ID.

        Returns:
            The list of messages.
        """
        get_query = gql('''
      query ($query: MessageQueryInput!) {
        messages(query: $query, sortBy: CREATED_AT_ASC) {
          role
          content
        }
      }
      ''')
        seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

        variables = {
            'query': {
                'user_sid': user_sid,
                'created_at_gt': seven_days_ago.isoformat()
            }
        }

        response = self._client.execute(get_query, variable_values=variables)
        return response['messages']
